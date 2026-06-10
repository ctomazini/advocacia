import frappe
from frappe import _
from frappe.utils import add_days, cstr, flt, getdate, now_datetime, today

# ── ignore_permissions justificativa ──────────────────────────────────
# As funções de sincronização (sincronizar_pagamentos_do_acordo,
# sincronizar_cobranca_atos, processar_pagamento_on_update) rodam como
# doc_events disparados pelo save do usuário no Acordo/Registro/Legal Payment.
# O sistema cria/atualiza Legal Payments filho em nome do usuário autenticado.
# O acesso ao doc-pai já foi validado pelo Frappe antes do doc_event.
# Por isso ignore_permissions=True é intencional nessas operações.
# ──────────────────────────────────────────────────────────────────────

STATUS_PARCELA_TO_PAGAMENTO = {
	"Pendente": "Pendente",
	"Vencido": "Vencido",
	"Recebido": "Recebido",
	"Repassado": "Repassado",
	"Cancelado": "Cancelado",
}

STATUS_PAGAMENTO_TO_PARCELA = {
	"Pendente": "Pendente",
	"Vencido": "Vencido",
	"Recebido": "Recebido",
	"Repassado": "Repassado",
	"Cancelado": "Cancelado",
	"Renegociado": "Pendente",
}

TIPO_HONORARIOS = "Honorários (Parcela)"
TIPO_ATOS = "Atos Advocatícios"


def is_pagamento_atos(pagamento):
	return (pagamento.get("origin_type") or "") == TIPO_ATOS


def is_pagamento_honorarios(pagamento):
	tipo = pagamento.get("origin_type") or TIPO_HONORARIOS
	return tipo == TIPO_HONORARIOS


def sincronizar_pagamentos_hook(doc, method=None):
	if frappe.flags.in_pagamento_sync:
		return
	frappe.flags.in_pagamento_sync = True
	try:
		sincronizar_pagamentos_do_acordo(doc)
	finally:
		frappe.flags.in_pagamento_sync = False


def sincronizar_pagamentos_do_acordo(acordo_doc, commit=False):
	"""Sincroniza parcelas do acordo com registros Legal Payment (idempotente)."""
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
	parcelas = acordo.get("fee_installments") or []
	active_origem_ids = set()
	criados = atualizados = cancelados = 0

	cliente = acordo.client
	servico = acordo.legal_case

	for idx, parcela in enumerate(parcelas, start=1):
		origem_id = parcela.installment_origin_id
		if not origem_id:
			continue
		active_origem_ids.add(origem_id)

		pagamento_name = frappe.db.get_value(
			"Legal Payment", {"installment_origin_id": origem_id}, "name"
		)
		payload = _parcela_to_pagamento_payload(acordo, parcela, idx, cliente, servico)

		if not pagamento_name:
			doc = frappe.get_doc({"doctype": "Legal Payment", **payload})
			doc.insert(ignore_permissions=True)
			_vincular_pagamento_na_parcela(origem_id, doc.name)
			criados += 1
			continue

		pagamento = frappe.get_doc("Legal Payment", pagamento_name)
		if is_pagamento_atos(pagamento):
			continue
		_vincular_pagamento_na_parcela(origem_id, pagamento_name)
		if _pode_atualizar_pagamento(pagamento):
			changed = _apply_pagamento_payload(pagamento, payload)
			if changed:
				pagamento.save(ignore_permissions=True)
				atualizados += 1
		elif pagamento.status not in ("Recebido", "Repassado", "Cancelado"):
			_sync_status_from_parcela(pagamento, parcela)

	cancelados += _cancelar_pagamentos_orfaos(acordo.name, active_origem_ids)

	frappe.logger().info(
		"Sync pagamentos acordo {0}: +{1} ~{2} cancelados {3}".format(
			acordo.name, criados, atualizados, cancelados
		)
	)
	return {"criados": criados, "atualizados": atualizados, "cancelados": cancelados}


def migrar_pagamentos_existentes():
	"""Patch: gera Legal Payments para todos os acordos (idempotente)."""
	acordos = frappe.get_all(
		"Fee Agreement",
		pluck="name",
		limit_page_length=0,  # patch — processa todos
	)
	total_criados = total_atualizados = 0
	for acordo_name in acordos:
		doc = frappe.get_doc("Fee Agreement", acordo_name)
		result = sincronizar_pagamentos_do_acordo(doc, commit=False)
		total_criados += result.get("criados", 0)
		total_atualizados += result.get("atualizados", 0)
	frappe.logger().info(
		"Migração pagamentos: {0} acordos, {1} criados, {2} atualizados".format(
			len(acordos), total_criados, total_atualizados
		)
	)


def sync_parcela_from_pagamento(pagamento):
	"""Propaga status do Legal Payment para a parcela contratual."""
	if is_pagamento_atos(pagamento):
		return
	if not pagamento.installment_origin_id:
		return
	if str(pagamento.installment_origin_id).startswith("ATOS-"):
		return

	parcela_name = frappe.db.get_value(
		"Fee Installment",
		{"installment_origin_id": pagamento.installment_origin_id},
		"name",
	)
	if not parcela_name:
		return

	updates = {}
	if pagamento.status == "Recebido":
		updates["status"] = "Recebido"
		updates["received_date"] = pagamento.received_date or today()
	elif pagamento.status == "Repassado":
		updates["status"] = "Repassado"
		updates["received_date"] = pagamento.received_date or today()
	elif pagamento.status == "Vencido":
		updates["status"] = "Vencido"
	elif pagamento.status == "Cancelado":
		updates["status"] = "Cancelado"
	elif pagamento.status == "Pendente":
		updates["status"] = "Pendente"

	if pagamento.name:
		updates["payment"] = pagamento.name

	if updates:
		frappe.db.set_value("Fee Installment", parcela_name, updates, update_modified=True)


def sync_pagamento_from_parcela(parcela):
	"""Propaga status da parcela contratual para o Legal Payment vinculado."""
	if not parcela.get("installment_origin_id"):
		return
	if str(parcela.installment_origin_id).startswith("ATOS-"):
		return

	pagamento_name = frappe.db.get_value(
		"Legal Payment", {"installment_origin_id": parcela.installment_origin_id}, "name"
	)
	if not pagamento_name:
		return

	pagamento = frappe.get_doc("Legal Payment", pagamento_name)
	if is_pagamento_atos(pagamento) or pagamento.status == "Cancelado":
		return
	if pagamento.manual_override or pagamento.status in ("Recebido", "Repassado"):
		_vincular_pagamento_na_parcela(parcela.installment_origin_id, pagamento_name)
		return

	new_status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	updates = {}
	if pagamento.status != new_status and pagamento.status in ("Pendente", "Vencido"):
		updates["status"] = new_status
	if parcela.status in ("Recebido", "Repassado") and parcela.get("received_date"):
		if not pagamento.received_date:
			updates["received_date"] = parcela.received_date

	_vincular_pagamento_na_parcela(parcela.installment_origin_id, pagamento_name)

	if not updates:
		return

	already_syncing = getattr(frappe.flags, "in_pagamento_sync", False)
	if not already_syncing:
		frappe.flags.in_pagamento_sync = True
	try:
		updates["synced_at"] = now_datetime()
		frappe.db.set_value("Legal Payment", pagamento_name, updates, update_modified=True)
	finally:
		if not already_syncing:
			frappe.flags.in_pagamento_sync = False


def _vincular_pagamento_na_parcela(parcela_origem_id, pagamento_name):
	"""Grava Link Legal Payment na linha da parcela contratual (via parcela_origem_id)."""
	if not parcela_origem_id or not pagamento_name:
		return
	parcela_name = frappe.db.get_value(
		"Fee Installment",
		{"installment_origin_id": parcela_origem_id},
		"name",
	)
	if not parcela_name:
		return
	current = frappe.db.get_value("Fee Installment", parcela_name, "payment")
	if current != pagamento_name:
		frappe.db.set_value(
			"Fee Installment",
			parcela_name,
			"payment",
			pagamento_name,
			update_modified=False,
		)


def _limpar_vinculo_pagamento_na_parcela(pagamento):
	"""Remove Link pagamento das parcelas antes de excluir (evita LinkExistsError)."""
	if not pagamento.name:
		return
	parcelas = frappe.get_all(
		"Fee Installment",
		filters={"payment": pagamento.name},
		pluck="name",
		limit_page_length=500,
	)
	for parcela_name in parcelas:
		frappe.db.set_value(
			"Fee Installment",
			parcela_name,
			"payment",
			"",
			update_modified=False,
		)


def on_pagamento_trash(doc, method=None):
	"""Impede exclusão de Legal Payment de honorários já recebido."""
	if is_pagamento_atos(doc):
		return

	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(
			_("Não é possível excluir Legal Payment de honorários com status '{0}'. "
			  "Cancele o pagamento primeiro.").format(doc.status),
			title=_("Exclusão Bloqueada"),
		)

	_limpar_vinculo_pagamento_na_parcela(doc)


def processar_pagamento_on_update(doc, method=None):
	"""Handler único de Legal Payment.on_update — orquestra tarefas e honorários na ordem original."""
	from advocacia.advocacia.tasks import on_pagamento_update as sync_tarefas_on_pagamento

	sync_tarefas_on_pagamento(doc, method)
	on_pagamento_update_honorarios(doc, method)


def on_pagamento_update_honorarios(doc, method=None):
	"""Propaga status do Legal Payment de honorários para parcela e recalcula acordo."""
	if getattr(frappe.flags, "in_pagamento_sync", False):
		return
	if is_pagamento_atos(doc):
		return

	sync_parcela_from_pagamento(doc)

	if not doc.fee_agreement:
		return
	if doc.status == "Cancelado":
		verificar_acordo_quitado(doc.fee_agreement)


def verificar_acordo_quitado(acordo_name):
	"""Recalcula status Quitado do acordo após cancelamento ou reversão."""
	if not acordo_name:
		return

	from advocacia.advocacia.tasks import _marcar_acordo_quitado_se_completo

	acordo_status = frappe.db.get_value(
		"Fee Agreement", acordo_name, "status"
	)
	if acordo_status == "Quitado":
		pagamentos = frappe.get_all(
			"Legal Payment",
			filters={
				"fee_agreement": acordo_name,
				"origin_type": ["in", [TIPO_HONORARIOS, ""]],
				"status": ["not in", ["Cancelado"]],
			},
			fields=["status"],
			limit_page_length=500,
		)
		if not pagamentos or not all(
			p.status in ("Recebido", "Repassado") for p in pagamentos
		):
			frappe.db.set_value(
				"Fee Agreement",
				acordo_name,
				"status",
				"Vigente",
				update_modified=True,
			)
			frappe.logger().info(
				"Acordo {0} revertido de Quitado para Vigente".format(acordo_name)
			)
			return

	_marcar_acordo_quitado_se_completo(acordo_name, usar_pagamentos=True)


@frappe.whitelist()
def resync_pagamentos_acordo(acordo_name: str) -> dict:
	"""Re-sincroniza pagamentos do Acordo sem precisar editar campos."""
	acordo = frappe.get_doc("Fee Agreement", acordo_name)
	frappe.has_permission(
		"Fee Agreement", "write", doc=acordo, throw=True
	)
	sincronizar_pagamentos_do_acordo(acordo)
	frappe.msgprint(
		_("Legal Payments re-sincronizados com sucesso."),
		title=_("Sincronização"),
		indicator="green",
	)
	return {"status": "ok"}


@frappe.whitelist()
def bulk_delete_pagamentos(names: str | list) -> dict:
	"""Exclusão em massa síncrona com feedback (contorna fila padrão do Frappe para >10)."""
	import json

	STATUS_BULK_PERMITIDOS = ("Pendente", "Cancelado")

	if isinstance(names, str):
		names = json.loads(names)
	if not names:
		frappe.throw(_("Nenhum pagamento selecionado."))
	frappe.has_permission("Legal Payment", "delete", throw=True)

	excluidos = []
	ignorados = []

	for name in names:
		if not frappe.db.exists("Legal Payment", name):
			ignorados.append({"name": name, "motivo": _("Registro não encontrado.")})
			continue

		doc = frappe.get_doc("Legal Payment", name)
		if doc.status not in STATUS_BULK_PERMITIDOS:
			if doc.status in ("Recebido", "Repassado"):
				motivo = _(
					"Status '{0}' não permite exclusão em massa. Cancele primeiro."
				).format(doc.status)
			else:
				motivo = _(
					"Status '{0}' não permite exclusão em massa. "
					"Exclua individualmente abrindo o registro."
				).format(doc.status)
			ignorados.append({"name": doc.name, "motivo": motivo})
			continue

		try:
			frappe.flags.in_bulk_delete = True
			frappe.delete_doc("Legal Payment", doc.name, force=0, ignore_permissions=False)
			excluidos.append(doc.name)
		except Exception as e:
			frappe.db.rollback()
			ignorados.append({"name": doc.name, "motivo": cstr(e)})

	return {
		"excluidos": excluidos,
		"ignorados": ignorados,
		"total": len(names),
	}


@frappe.whitelist()
def gerar_pagamento_atos(registro_name: str, due_date: str | None = None) -> dict:
	"""Sincroniza atos pendentes com o Legal Payment aberto do registro (idempotente)."""
	frappe.has_permission("Service Record", "write", doc=registro_name, throw=True)
	return sincronizar_pagamento_atos(registro_name, due_date)


@frappe.whitelist()
def sincronizar_pagamento_atos(registro_name: str, due_date: str | None = None) -> dict:
	"""Upsert: atualiza Legal Payment Atos aberto ou cria um novo lote fechado."""
	frappe.has_permission("Service Record", "write", throw=True)

	registro = frappe.get_doc("Service Record", registro_name)
	vencimento = getdate(due_date or registro.billing_due_date or add_days(today(), 30))

	pagamento_aberto = _get_pagamento_atos_aberto(registro.name)
	criado = False

	if pagamento_aberto:
		pagamento = frappe.get_doc("Legal Payment", pagamento_aberto)
		incluidos, novos = _classificar_atos_para_sync(registro, pagamento.name)
		if not novos and not incluidos:
			frappe.throw(_("Não há atos para sincronizar na cobrança."))
		atos_faturados = incluidos + novos
	else:
		novos = [
			ato
			for ato in registro.acts or []
			if ato.status == "Pendente" and flt(ato.amount) > 0
		]
		if not novos:
			frappe.throw(_("Não há atos pendentes para cobrar."))
		atos_faturados = novos
		pagamento = None

	total = sum(flt(ato.amount) for ato in atos_faturados)
	observacoes = _montar_observacoes_atos(atos_faturados)

	if pagamento:
		if pagamento.status not in ("Pendente", "Vencido"):
			frappe.throw(
				_("Legal Payment {0} não está aberto para sincronização.").format(pagamento.name)
			)
		pagamento.amount = total
		pagamento.remarks = observacoes
		pagamento.due_date = vencimento
		pagamento.synced_at = now_datetime()
		pagamento.save(ignore_permissions=True)
	else:
		criado = True
		origem_id = _gerar_parcela_origem_id_atos(registro.name)
		pagamento = frappe.get_doc(
			{
				"doctype": "Legal Payment",
				"origin_type": TIPO_ATOS,
				"service_record": registro.name,
				"legal_case": registro.legal_case,
				"client": registro.client,
				"installment_origin_id": origem_id,
				"description": _("Atos — {0}").format(registro.name)[:140],
				"amount": total,
				"due_date": vencimento,
				"status": "Pendente",
				"remarks": observacoes,
			}
		)
		pagamento.insert(ignore_permissions=True)

	for ato in novos:
		ato.status = "Cobrado"
		ato.payment = pagamento.name

	registro.last_payment = pagamento.name
	registro._calcular_totais()
	registro._atualizar_status()
	frappe.flags.in_atos_cobranca_sync = True
	try:
		registro.flags.ignore_validate = True
		registro.save(ignore_permissions=True)
	finally:
		frappe.flags.in_atos_cobranca_sync = False

	acao = "criado" if criado else "atualizado"
	frappe.logger().info(
		"Cobrança atos {0} {1}: pagamento {2}, {3} ato(s), R$ {4}".format(
			registro.name, acao, pagamento.name, len(atos_faturados), total
		)
	)

	return {
		"success": True,
		"criado": criado,
		"payment": pagamento.name,
		"total": total,
		"qtd_atos": len(atos_faturados),
		"qtd_novos": len(novos),
	}


def _get_pagamento_atos_aberto(registro_name):
	return frappe.db.get_value(
		"Legal Payment",
		{
			"service_record": registro_name,
			"origin_type": TIPO_ATOS,
			"status": ["in", ["Pendente", "Vencido"]],
		},
		"name",
		order_by="creation desc",
	)


def _classificar_atos_para_sync(registro, pagamento_name):
	incluidos = []
	novos = []
	for ato in registro.acts or []:
		if ato.status == "Cobrado" and ato.payment == pagamento_name:
			incluidos.append(ato)
		elif ato.status == "Pendente" and flt(ato.amount) > 0:
			novos.append(ato)
	return incluidos, novos


def _montar_observacoes_atos(atos):
	partes = []
	for ato in atos:
		desc = ato.get("description") or ato.get("description") or ""
		partes.append(
			"{0}: {1} (R$ {2:.2f})".format(ato.type or _("Ato"), desc, flt(ato.amount))
		)
	return "\n".join(partes)


def _gerar_parcela_origem_id_atos(registro_name):
	"""ID determinístico: ATOS-{registro}, sequência -02 se lote anterior existir."""
	base = "ATOS-{0}".format(registro_name)
	if not frappe.db.exists("Legal Payment", {"installment_origin_id": base}):
		return base
	seq = 2
	while frappe.db.exists("Legal Payment", {"installment_origin_id": "{0}-{1:02d}".format(base, seq)}):
		seq += 1
	return "{0}-{1:02d}".format(base, seq)


def reverter_atos_do_pagamento(pagamento):
	"""Devolve atos para Pendente quando Legal Payment de origem Atos é cancelado."""
	liberar_vinculos_pagamento_atos(pagamento, revert_atos=True)


def liberar_vinculos_pagamento_atos(pagamento, revert_atos=True):
	"""Desvincula Legal Payment Atos do Registro (atos + ultimo_pagamento). Usado no cancelamento e on_trash."""
	if not is_pagamento_atos(pagamento):
		return
	if not pagamento.service_record:
		return

	registro_name = pagamento.service_record
	changed = False

	if revert_atos:
		registro = frappe.get_doc("Service Record", registro_name)
		for ato in registro.acts or []:
			if ato.payment == pagamento.name and ato.status == "Cobrado":
				ato.status = "Pendente"
				ato.payment = None
				changed = True

		if changed:
			frappe.flags.in_atos_cobranca_sync = True
			try:
				registro.flags.ignore_validate = True
				registro.save(ignore_permissions=True)
			finally:
				frappe.flags.in_atos_cobranca_sync = False
			frappe.logger().info(
				"Atos revertidos para Pendente — pagamento {0}".format(pagamento.name)
			)

	_limpar_ultimo_pagamento_se_apontar(registro_name, pagamento.name)


def _limpar_ultimo_pagamento_se_apontar(registro_name, pagamento_name):
	if frappe.db.get_value("Service Record", registro_name, "last_payment") != pagamento_name:
		return

	outro = frappe.db.get_value(
		"Legal Payment",
		{
			"service_record": registro_name,
			"origin_type": TIPO_ATOS,
			"name": ["!=", pagamento_name],
			"status": ["not in", ["Cancelado"]],
		},
		"name",
		order_by="modified desc",
	)
	frappe.db.set_value(
		"Service Record",
		registro_name,
		"last_payment",
		outro,
		update_modified=False,
	)


@frappe.whitelist()
def cancelar_cobranca_pagamento_atos(pagamento_name: str) -> dict:
	"""Cancela cobrança de atos e libera vínculos no Registro."""
	frappe.has_permission("Legal Payment", "write", throw=True)

	pagamento = frappe.get_doc("Legal Payment", pagamento_name)
	if not is_pagamento_atos(pagamento):
		frappe.throw(_("Este pagamento não é de origem Atos Advocatícios."))

	if pagamento.status == "Cancelado":
		frappe.throw(_("Legal Payment já está cancelado."))

	if pagamento.status in ("Recebido", "Repassado"):
		frappe.throw(
			_("Legal Payment recebido não pode ser cancelado. Estorne manualmente se necessário."),
			title=_("Operação não permitida"),
		)

	pagamento.status = "Cancelado"
	pagamento.save(ignore_permissions=False)

	return {
		"success": True,
		"payment": pagamento.name,
		"service_record": pagamento.service_record,
	}


@frappe.whitelist()
def cancelar_pagamento_honorarios(pagamento_name: str) -> dict:
	"""Cancela pagamento de honorários e propaga status para a parcela do acordo."""
	frappe.has_permission("Legal Payment", "write", throw=True)

	pagamento = frappe.get_doc("Legal Payment", pagamento_name)
	if is_pagamento_atos(pagamento):
		frappe.throw(_("Este pagamento é de Atos Advocatícios. Use o botão Cancelar Legal Payment no form de Atos."))

	if pagamento.status == "Cancelado":
		frappe.throw(_("Legal Payment já está cancelado."))

	pagamento.status = "Cancelado"
	pagamento.save(ignore_permissions=False)

	return {
		"success": True,
		"payment": pagamento.name,
		"fee_agreement": pagamento.fee_agreement,
	}


def _as_acordo_doc(acordo_doc):
	if isinstance(acordo_doc, str):
		return frappe.get_doc("Fee Agreement", acordo_doc)
	if getattr(acordo_doc, "doctype", None) == "Fee Agreement":
		return acordo_doc
	return None


def _ensure_parcela_origem_ids(acordo):
	for parcela in acordo.get("fee_installments") or []:
		if parcela.installment_origin_id:
			continue
		new_id = _gerar_parcela_origem_id()
		parcela.installment_origin_id = new_id
		if parcela.name:
			frappe.db.set_value(
				"Fee Installment",
				parcela.name,
				"installment_origin_id",
				new_id,
				update_modified=False,
			)


def _gerar_parcela_origem_id():
	return "PARC-{0}".format(frappe.generate_hash(length=12))


def _parcela_to_pagamento_payload(acordo, parcela, idx, cliente, servico):
	descricao = parcela.get("description") or parcela.get("description") or ""
	status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	valor_recebido = flt(parcela.total_amount) if status in ("Recebido", "Repassado") else 0

	return {
		"origin_type": TIPO_HONORARIOS,
		"fee_agreement": acordo.name,
		"legal_case": servico,
		"client": cliente,
		"installment_origin_id": parcela.installment_origin_id,
		"installment_number": idx,
		"description": descricao,
		"amount": flt(parcela.total_amount),
		"received_amount": valor_recebido,
		"due_date": parcela.due_date,
		"received_date": parcela.received_date,
		"status": status,
		"remarks": parcela.get("remarks") or "",
		"synced_at": now_datetime(),
	}


def _pode_atualizar_pagamento(pagamento):
	if is_pagamento_atos(pagamento):
		return False
	if pagamento.status == "Cancelado":
		return False
	if pagamento.manual_override:
		return False
	if pagamento.status in ("Recebido", "Repassado"):
		return False
	if pagamento.received_date:
		return False
	return True


def _apply_pagamento_payload(pagamento, payload):
	changed = False
	for field in (
		"origin_type",
		"fee_agreement",
		"legal_case",
		"client",
		"installment_number",
		"description",
		"amount",
		"due_date",
		"remarks",
	):
		if pagamento.get(field) != payload.get(field):
			pagamento.set(field, payload.get(field))
			changed = True
	if pagamento.status != payload.get("status") and pagamento.status in ("Pendente", "Vencido"):
		pagamento.status = payload.get("status")
		changed = True
	pagamento.synced_at = now_datetime()
	return changed


def _sync_status_from_parcela(pagamento, parcela):
	if is_pagamento_atos(pagamento):
		return
	if pagamento.status == "Cancelado":
		return
	new_status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	if pagamento.status != new_status and pagamento.status in ("Pendente", "Vencido"):
		pagamento.status = new_status
		pagamento.synced_at = now_datetime()
		pagamento.save(ignore_permissions=True)


def _cancelar_pagamentos_orfaos(acordo_name, active_origem_ids):
	cancelados = 0
	filters = {
		"fee_agreement": acordo_name,
		"origin_type": ["in", [TIPO_HONORARIOS, ""]],
	}
	if active_origem_ids:
		filters["installment_origin_id"] = ["not in", list(active_origem_ids)]

	orphans = frappe.get_all(
		"Legal Payment",
		filters=filters,
		fields=["name", "status", "received_date", "installment_origin_id"],
		limit_page_length=500,
	)
	for row in orphans:
		if row.status in ("Recebido", "Repassado") or row.received_date:
			frappe.logger().info(
				"Legal Payment {0} órfão preservado (já recebido). Parcela origem: {1}".format(
					row.name, row.installment_origin_id
				)
			)
			continue
		if row.status != "Cancelado":
			frappe.db.set_value(
				"Legal Payment",
				row.name,
				{"status": "Cancelado", "synced_at": now_datetime()},
				update_modified=True,
			)
			cancelados += 1
	return cancelados
