import frappe
from frappe.utils import flt, now_datetime, today

STATUS_PARCELA_TO_PAGAMENTO = {
	"Pendente": "Pendente",
	"Vencida": "Vencido",
	"Recebida": "Recebido",
	"Repassada": "Repassado",
	"Cancelada": "Cancelado",
}

STATUS_PAGAMENTO_TO_PARCELA = {
	"Pendente": "Pendente",
	"Vencido": "Vencida",
	"Recebido": "Recebida",
	"Repassado": "Repassada",
	"Cancelado": "Cancelada",
	"Renegociado": "Pendente",
}


def sincronizar_pagamentos_hook(doc, method=None):
	if frappe.flags.in_pagamento_sync:
		return
	frappe.flags.in_pagamento_sync = True
	try:
		sincronizar_pagamentos_do_acordo(doc)
	finally:
		frappe.flags.in_pagamento_sync = False


def sincronizar_pagamentos_do_acordo(acordo_doc, commit=False):
	"""Sincroniza parcelas do acordo com registros Pagamento (idempotente)."""
	acordo = _as_acordo_doc(acordo_doc)
	if not acordo or not acordo.name:
		return {"criados": 0, "atualizados": 0, "cancelados": 0}

	prev_flag = getattr(frappe.flags, "in_pagamento_sync", False)
	frappe.flags.in_pagamento_sync = True
	try:
		return _sincronizar_pagamentos_do_acordo_impl(acordo, commit)
	finally:
		frappe.flags.in_pagamento_sync = prev_flag


def _sincronizar_pagamentos_do_acordo_impl(acordo, commit=False):
	_ensure_parcela_origem_ids(acordo)
	parcelas = acordo.get("table_ztjx") or []
	active_origem_ids = set()
	criados = atualizados = cancelados = 0

	cliente = acordo.cliente
	servico = acordo.servico

	for idx, parcela in enumerate(parcelas, start=1):
		origem_id = parcela.parcela_origem_id
		if not origem_id:
			continue
		active_origem_ids.add(origem_id)

		pagamento_name = frappe.db.get_value(
			"Pagamento", {"parcela_origem_id": origem_id}, "name"
		)
		payload = _parcela_to_pagamento_payload(acordo, parcela, idx, cliente, servico)

		if not pagamento_name:
			doc = frappe.get_doc({"doctype": "Pagamento", **payload})
			doc.insert(ignore_permissions=True)
			criados += 1
			continue

		pagamento = frappe.get_doc("Pagamento", pagamento_name)
		if _pode_atualizar_pagamento(pagamento):
			changed = _apply_pagamento_payload(pagamento, payload)
			if changed:
				pagamento.save(ignore_permissions=True)
				atualizados += 1
		elif pagamento.status not in ("Recebido", "Repassado"):
			_sync_status_from_parcela(pagamento, parcela)

	cancelados += _cancelar_pagamentos_orfaos(acordo.name, active_origem_ids)

	if commit:
		frappe.db.commit()

	frappe.logger().info(
		"Sync pagamentos acordo {0}: +{1} ~{2} cancelados {3}".format(
			acordo.name, criados, atualizados, cancelados
		)
	)
	return {"criados": criados, "atualizados": atualizados, "cancelados": cancelados}


def migrar_pagamentos_existentes():
	"""Patch: gera Pagamentos para todos os acordos (idempotente)."""
	acordos = frappe.get_all("Acordo de Honorarios Processuais", pluck="name")
	total_criados = total_atualizados = 0
	for acordo_name in acordos:
		doc = frappe.get_doc("Acordo de Honorarios Processuais", acordo_name)
		result = sincronizar_pagamentos_do_acordo(doc, commit=False)
		total_criados += result.get("criados", 0)
		total_atualizados += result.get("atualizados", 0)
	frappe.db.commit()
	frappe.logger().info(
		"Migração pagamentos: {0} acordos, {1} criados, {2} atualizados".format(
			len(acordos), total_criados, total_atualizados
		)
	)


def sync_parcela_from_pagamento(pagamento):
	"""Propaga recebimento do Pagamento para a parcela contratual."""
	if not pagamento.parcela_origem_id:
		return
	parcela_name = frappe.db.get_value(
		"Parcela de Honorarios",
		{"parcela_origem_id": pagamento.parcela_origem_id},
		"name",
	)
	if not parcela_name:
		return

	updates = {}
	if pagamento.status == "Recebido":
		updates["status"] = "Recebida"
		updates["data_recebimento"] = pagamento.data_recebimento or today()
	elif pagamento.status == "Repassado":
		updates["status"] = "Repassada"
		updates["data_recebimento"] = pagamento.data_recebimento or today()
	elif pagamento.status == "Vencido":
		updates["status"] = "Vencida"
	elif pagamento.status == "Cancelado":
		updates["status"] = "Cancelada"
	elif pagamento.status == "Pendente":
		updates["status"] = "Pendente"

	if updates:
		frappe.db.set_value("Parcela de Honorarios", parcela_name, updates, update_modified=True)


def _as_acordo_doc(acordo_doc):
	if isinstance(acordo_doc, str):
		return frappe.get_doc("Acordo de Honorarios Processuais", acordo_doc)
	if getattr(acordo_doc, "doctype", None) == "Acordo de Honorarios Processuais":
		return acordo_doc
	return None


def _ensure_parcela_origem_ids(acordo):
	for parcela in acordo.get("table_ztjx") or []:
		if parcela.parcela_origem_id:
			continue
		new_id = _gerar_parcela_origem_id()
		parcela.parcela_origem_id = new_id
		if parcela.name:
			frappe.db.set_value(
				"Parcela de Honorarios",
				parcela.name,
				"parcela_origem_id",
				new_id,
				update_modified=False,
			)


def _gerar_parcela_origem_id():
	return "PARC-{0}".format(frappe.generate_hash(length=12))


def _parcela_to_pagamento_payload(acordo, parcela, idx, cliente, servico):
	descricao = parcela.get("descrição") or parcela.get("descricao") or ""
	status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	valor_recebido = flt(parcela.valor_total) if status in ("Recebido", "Repassado") else 0

	return {
		"acordo": acordo.name,
		"servico": servico,
		"cliente": cliente,
		"parcela_origem_id": parcela.parcela_origem_id,
		"numero_parcela": idx,
		"descricao": descricao,
		"valor": flt(parcela.valor_total),
		"valor_recebido": valor_recebido,
		"data_vencimento": parcela.vencimento,
		"data_recebimento": parcela.data_recebimento,
		"status": status,
		"observacoes": parcela.get("observacao") or "",
		"sincronizado_em": now_datetime(),
	}


def _pode_atualizar_pagamento(pagamento):
	if pagamento.manual_override:
		return False
	if pagamento.status in ("Recebido", "Repassado"):
		return False
	if pagamento.data_recebimento:
		return False
	return True


def _apply_pagamento_payload(pagamento, payload):
	changed = False
	for field in (
		"acordo",
		"servico",
		"cliente",
		"numero_parcela",
		"descricao",
		"valor",
		"data_vencimento",
		"observacoes",
	):
		if pagamento.get(field) != payload.get(field):
			pagamento.set(field, payload.get(field))
			changed = True
	if pagamento.status != payload.get("status") and pagamento.status in ("Pendente", "Vencido"):
		pagamento.status = payload.get("status")
		changed = True
	pagamento.sincronizado_em = now_datetime()
	return changed


def _sync_status_from_parcela(pagamento, parcela):
	new_status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	if pagamento.status != new_status and pagamento.status in ("Pendente", "Vencido"):
		pagamento.status = new_status
		pagamento.sincronizado_em = now_datetime()
		pagamento.save(ignore_permissions=True)


def _cancelar_pagamentos_orfaos(acordo_name, active_origem_ids):
	cancelados = 0
	filters = {"acordo": acordo_name}
	if active_origem_ids:
		filters["parcela_origem_id"] = ["not in", list(active_origem_ids)]

	orphans = frappe.get_all(
		"Pagamento",
		filters=filters,
		fields=["name", "status", "data_recebimento", "parcela_origem_id"],
	)
	for row in orphans:
		if row.status in ("Recebido", "Repassado") or row.data_recebimento:
			frappe.logger().info(
				"Pagamento {0} órfão preservado (já recebido). Parcela origem: {1}".format(
					row.name, row.parcela_origem_id
				)
			)
			continue
		if row.status != "Cancelado":
			frappe.db.set_value(
				"Pagamento",
				row.name,
				{"status": "Cancelado", "sincronizado_em": now_datetime()},
				update_modified=True,
			)
			cancelados += 1
	return cancelados
