import frappe
from frappe import _
from frappe.utils import add_days, cstr, flt, getdate, now_datetime, today

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
	return (pagamento.get("tipo_origem") or "") == TIPO_ATOS


def is_pagamento_honorarios(pagamento):
	tipo = pagamento.get("tipo_origem") or TIPO_HONORARIOS
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
	parcelas = acordo.get("parcelas") or []
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
			_vincular_pagamento_na_parcela(origem_id, doc.name)
			criados += 1
			continue

		pagamento = frappe.get_doc("Pagamento", pagamento_name)
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
	"""Patch: gera Pagamentos para todos os acordos (idempotente)."""
	acordos = frappe.get_all("Acordo de Honorarios Processuais", pluck="name")
	total_criados = total_atualizados = 0
	for acordo_name in acordos:
		doc = frappe.get_doc("Acordo de Honorarios Processuais", acordo_name)
		result = sincronizar_pagamentos_do_acordo(doc, commit=False)
		total_criados += result.get("criados", 0)
		total_atualizados += result.get("atualizados", 0)
	frappe.logger().info(
		"Migração pagamentos: {0} acordos, {1} criados, {2} atualizados".format(
			len(acordos), total_criados, total_atualizados
		)
	)


def sync_parcela_from_pagamento(pagamento):
	"""Propaga status do Pagamento para a parcela contratual."""
	if is_pagamento_atos(pagamento):
		return
	if not pagamento.parcela_origem_id:
		return
	if str(pagamento.parcela_origem_id).startswith("ATOS-"):
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
		updates["status"] = "Recebido"
		updates["data_recebimento"] = pagamento.data_recebimento or today()
	elif pagamento.status == "Repassado":
		updates["status"] = "Repassado"
		updates["data_recebimento"] = pagamento.data_recebimento or today()
	elif pagamento.status == "Vencido":
		updates["status"] = "Vencido"
	elif pagamento.status == "Cancelado":
		updates["status"] = "Cancelado"
	elif pagamento.status == "Pendente":
		updates["status"] = "Pendente"

	if pagamento.name:
		updates["pagamento"] = pagamento.name

	if updates:
		frappe.db.set_value("Parcela de Honorarios", parcela_name, updates, update_modified=True)


def sync_pagamento_from_parcela(parcela):
	"""Propaga status da parcela contratual para o Pagamento vinculado."""
	if not parcela.get("parcela_origem_id"):
		return
	if str(parcela.parcela_origem_id).startswith("ATOS-"):
		return

	pagamento_name = frappe.db.get_value(
		"Pagamento", {"parcela_origem_id": parcela.parcela_origem_id}, "name"
	)
	if not pagamento_name:
		return

	pagamento = frappe.get_doc("Pagamento", pagamento_name)
	if is_pagamento_atos(pagamento) or pagamento.status == "Cancelado":
		return
	if pagamento.manual_override or pagamento.status in ("Recebido", "Repassado"):
		_vincular_pagamento_na_parcela(parcela.parcela_origem_id, pagamento_name)
		return

	new_status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	updates = {}
	if pagamento.status != new_status and pagamento.status in ("Pendente", "Vencido"):
		updates["status"] = new_status
	if parcela.status in ("Recebido", "Repassado") and parcela.get("data_recebimento"):
		if not pagamento.data_recebimento:
			updates["data_recebimento"] = parcela.data_recebimento

	_vincular_pagamento_na_parcela(parcela.parcela_origem_id, pagamento_name)

	if not updates:
		return

	already_syncing = getattr(frappe.flags, "in_pagamento_sync", False)
	if not already_syncing:
		frappe.flags.in_pagamento_sync = True
	try:
		updates["sincronizado_em"] = now_datetime()
		frappe.db.set_value("Pagamento", pagamento_name, updates, update_modified=True)
	finally:
		if not already_syncing:
			frappe.flags.in_pagamento_sync = False


def _vincular_pagamento_na_parcela(parcela_origem_id, pagamento_name):
	"""Grava Link Pagamento na linha da parcela contratual (via parcela_origem_id)."""
	if not parcela_origem_id or not pagamento_name:
		return
	parcela_name = frappe.db.get_value(
		"Parcela de Honorarios",
		{"parcela_origem_id": parcela_origem_id},
		"name",
	)
	if not parcela_name:
		return
	current = frappe.db.get_value("Parcela de Honorarios", parcela_name, "pagamento")
	if current != pagamento_name:
		frappe.db.set_value(
			"Parcela de Honorarios",
			parcela_name,
			"pagamento",
			pagamento_name,
			update_modified=False,
		)


def _limpar_vinculo_pagamento_na_parcela(pagamento):
	"""Remove Link pagamento das parcelas antes de excluir (evita LinkExistsError)."""
	if not pagamento.name:
		return
	parcelas = frappe.get_all(
		"Parcela de Honorarios",
		filters={"pagamento": pagamento.name},
		pluck="name",
	)
	for parcela_name in parcelas:
		frappe.db.set_value(
			"Parcela de Honorarios",
			parcela_name,
			"pagamento",
			"",
			update_modified=False,
		)


def on_pagamento_trash(doc, method=None):
	"""Impede exclusão de Pagamento de honorários já recebido."""
	if is_pagamento_atos(doc):
		return

	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(
			_("Não é possível excluir Pagamento de honorários com status '{0}'. "
			  "Cancele o pagamento primeiro.").format(doc.status),
			title=_("Exclusão Bloqueada"),
		)

	_limpar_vinculo_pagamento_na_parcela(doc)


def processar_pagamento_on_update(doc, method=None):
	"""Handler único de Pagamento.on_update — orquestra tarefas e honorários na ordem original."""
	from advocacia.advocacia.tasks import on_pagamento_update as sync_tarefas_on_pagamento

	sync_tarefas_on_pagamento(doc, method)
	on_pagamento_update_honorarios(doc, method)


def on_pagamento_update_honorarios(doc, method=None):
	"""Propaga status do Pagamento de honorários para parcela e recalcula acordo."""
	if getattr(frappe.flags, "in_pagamento_sync", False):
		return
	if is_pagamento_atos(doc):
		return

	sync_parcela_from_pagamento(doc)

	if not doc.acordo:
		return
	if doc.status == "Cancelado":
		verificar_acordo_quitado(doc.acordo)


def verificar_acordo_quitado(acordo_name):
	"""Recalcula status Quitado do acordo após cancelamento ou reversão."""
	if not acordo_name:
		return

	from advocacia.advocacia.tasks import _marcar_acordo_quitado_se_completo

	acordo_status = frappe.db.get_value(
		"Acordo de Honorarios Processuais", acordo_name, "status"
	)
	if acordo_status == "Quitado":
		pagamentos = frappe.get_all(
			"Pagamento",
			filters={
				"acordo": acordo_name,
				"tipo_origem": ["in", [TIPO_HONORARIOS, ""]],
				"status": ["not in", ["Cancelado"]],
			},
			fields=["status"],
		)
		if not pagamentos or not all(
			p.status in ("Recebido", "Repassado") for p in pagamentos
		):
			frappe.db.set_value(
				"Acordo de Honorarios Processuais",
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
def resync_pagamentos_acordo(acordo_name):
	"""Re-sincroniza pagamentos do Acordo sem precisar editar campos."""
	acordo = frappe.get_doc("Acordo de Honorarios Processuais", acordo_name)
	frappe.has_permission(
		"Acordo de Honorarios Processuais", "write", doc=acordo, throw=True
	)
	sincronizar_pagamentos_do_acordo(acordo, commit=True)
	frappe.msgprint(
		_("Pagamentos re-sincronizados com sucesso."),
		title=_("Sincronização"),
		indicator="green",
	)
	return {"status": "ok"}


@frappe.whitelist()
def bulk_delete_pagamentos(names):
	"""Exclusão em massa síncrona com feedback (contorna fila padrão do Frappe para >10)."""
	import json

	STATUS_BULK_PERMITIDOS = ("Pendente", "Cancelado")

	if isinstance(names, str):
		names = json.loads(names)
	if not names:
		frappe.throw(_("Nenhum pagamento selecionado."))
	frappe.has_permission("Pagamento", "delete", throw=True)

	excluidos = []
	ignorados = []

	for name in names:
		if not frappe.db.exists("Pagamento", name):
			ignorados.append({"name": name, "motivo": _("Registro não encontrado.")})
			continue

		doc = frappe.get_doc("Pagamento", name)
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
			frappe.delete_doc("Pagamento", doc.name, force=0, ignore_permissions=False)
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
def gerar_pagamento_atos(registro_name, data_vencimento=None):
	"""Sincroniza atos pendentes com o Pagamento aberto do registro (idempotente)."""
	return sincronizar_pagamento_atos(registro_name, data_vencimento)


@frappe.whitelist()
def sincronizar_pagamento_atos(registro_name, data_vencimento=None):
	"""Upsert: atualiza Pagamento Atos aberto ou cria um novo lote fechado."""
	if not frappe.has_permission("Registro de Atos", "write"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	registro = frappe.get_doc("Registro de Atos", registro_name)
	vencimento = getdate(data_vencimento or registro.data_vencimento_cobranca or add_days(today(), 30))

	pagamento_aberto = _get_pagamento_atos_aberto(registro.name)
	criado = False

	if pagamento_aberto:
		pagamento = frappe.get_doc("Pagamento", pagamento_aberto)
		incluidos, novos = _classificar_atos_para_sync(registro, pagamento.name)
		if not novos and not incluidos:
			frappe.throw(_("Não há atos para sincronizar na cobrança."))
		atos_faturados = incluidos + novos
	else:
		novos = [
			ato
			for ato in registro.atos or []
			if ato.status == "Pendente" and flt(ato.valor) > 0
		]
		if not novos:
			frappe.throw(_("Não há atos pendentes para cobrar."))
		atos_faturados = novos
		pagamento = None

	total = sum(flt(ato.valor) for ato in atos_faturados)
	observacoes = _montar_observacoes_atos(atos_faturados)

	if pagamento:
		if pagamento.status not in ("Pendente", "Vencido"):
			frappe.throw(
				_("Pagamento {0} não está aberto para sincronização.").format(pagamento.name)
			)
		pagamento.valor = total
		pagamento.observacoes = observacoes
		pagamento.data_vencimento = vencimento
		pagamento.sincronizado_em = now_datetime()
		pagamento.save(ignore_permissions=True)
	else:
		criado = True
		origem_id = _gerar_parcela_origem_id_atos(registro.name)
		pagamento = frappe.get_doc(
			{
				"doctype": "Pagamento",
				"tipo_origem": TIPO_ATOS,
				"registro_atos": registro.name,
				"servico": registro.servico,
				"cliente": registro.cliente,
				"parcela_origem_id": origem_id,
				"descricao": _("Atos — {0}").format(registro.name)[:140],
				"valor": total,
				"data_vencimento": vencimento,
				"status": "Pendente",
				"observacoes": observacoes,
			}
		)
		pagamento.insert(ignore_permissions=True)

	for ato in novos:
		ato.status = "Cobrado"
		ato.cobranca_id = pagamento.name

	registro.ultimo_pagamento = pagamento.name
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
		"pagamento": pagamento.name,
		"total": total,
		"qtd_atos": len(atos_faturados),
		"qtd_novos": len(novos),
	}


def _get_pagamento_atos_aberto(registro_name):
	return frappe.db.get_value(
		"Pagamento",
		{
			"registro_atos": registro_name,
			"tipo_origem": TIPO_ATOS,
			"status": ["in", ["Pendente", "Vencido"]],
		},
		"name",
		order_by="creation desc",
	)


def _classificar_atos_para_sync(registro, pagamento_name):
	incluidos = []
	novos = []
	for ato in registro.atos or []:
		if ato.status == "Cobrado" and ato.cobranca_id == pagamento_name:
			incluidos.append(ato)
		elif ato.status == "Pendente" and flt(ato.valor) > 0:
			novos.append(ato)
	return incluidos, novos


def _montar_observacoes_atos(atos):
	partes = []
	for ato in atos:
		desc = ato.get("descrição") or ato.get("descricao") or ""
		partes.append(
			"{0}: {1} (R$ {2:.2f})".format(ato.tipo or _("Ato"), desc, flt(ato.valor))
		)
	return "\n".join(partes)


def _gerar_parcela_origem_id_atos(registro_name):
	"""ID determinístico: ATOS-{registro}, sequência -02 se lote anterior existir."""
	base = "ATOS-{0}".format(registro_name)
	if not frappe.db.exists("Pagamento", {"parcela_origem_id": base}):
		return base
	seq = 2
	while frappe.db.exists("Pagamento", {"parcela_origem_id": "{0}-{1:02d}".format(base, seq)}):
		seq += 1
	return "{0}-{1:02d}".format(base, seq)


def reverter_atos_do_pagamento(pagamento):
	"""Devolve atos para Pendente quando Pagamento de origem Atos é cancelado."""
	liberar_vinculos_pagamento_atos(pagamento, revert_atos=True)


def liberar_vinculos_pagamento_atos(pagamento, revert_atos=True):
	"""Desvincula Pagamento Atos do Registro (atos + ultimo_pagamento). Usado no cancelamento e on_trash."""
	if not is_pagamento_atos(pagamento):
		return
	if not pagamento.registro_atos:
		return

	registro_name = pagamento.registro_atos
	changed = False

	if revert_atos:
		registro = frappe.get_doc("Registro de Atos", registro_name)
		for ato in registro.atos or []:
			if ato.cobranca_id == pagamento.name and ato.status == "Cobrado":
				ato.status = "Pendente"
				ato.cobranca_id = None
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
	if frappe.db.get_value("Registro de Atos", registro_name, "ultimo_pagamento") != pagamento_name:
		return

	outro = frappe.db.get_value(
		"Pagamento",
		{
			"registro_atos": registro_name,
			"tipo_origem": TIPO_ATOS,
			"name": ["!=", pagamento_name],
			"status": ["not in", ["Cancelado"]],
		},
		"name",
		order_by="modified desc",
	)
	frappe.db.set_value(
		"Registro de Atos",
		registro_name,
		"ultimo_pagamento",
		outro,
		update_modified=False,
	)


@frappe.whitelist()
def cancelar_cobranca_pagamento_atos(pagamento_name):
	"""Cancela cobrança de atos e libera vínculos no Registro."""
	if not frappe.has_permission("Pagamento", "write"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	pagamento = frappe.get_doc("Pagamento", pagamento_name)
	if not is_pagamento_atos(pagamento):
		frappe.throw(_("Este pagamento não é de origem Atos Advocatícios."))

	if pagamento.status == "Cancelado":
		frappe.throw(_("Pagamento já está cancelado."))

	if pagamento.status in ("Recebido", "Repassado"):
		frappe.throw(
			_("Pagamento recebido não pode ser cancelado. Estorne manualmente se necessário."),
			title=_("Operação não permitida"),
		)

	pagamento.status = "Cancelado"
	pagamento.save(ignore_permissions=False)

	return {
		"success": True,
		"pagamento": pagamento.name,
		"registro_atos": pagamento.registro_atos,
	}


@frappe.whitelist()
def cancelar_pagamento_honorarios(pagamento_name):
	"""Cancela pagamento de honorários e propaga status para a parcela do acordo."""
	if not frappe.has_permission("Pagamento", "write"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	pagamento = frappe.get_doc("Pagamento", pagamento_name)
	if is_pagamento_atos(pagamento):
		frappe.throw(_("Este pagamento é de Atos Advocatícios. Use o botão Cancelar Pagamento no form de Atos."))

	if pagamento.status == "Cancelado":
		frappe.throw(_("Pagamento já está cancelado."))

	pagamento.status = "Cancelado"
	pagamento.save(ignore_permissions=False)

	return {
		"success": True,
		"pagamento": pagamento.name,
		"acordo": pagamento.acordo,
	}


def _as_acordo_doc(acordo_doc):
	if isinstance(acordo_doc, str):
		return frappe.get_doc("Acordo de Honorarios Processuais", acordo_doc)
	if getattr(acordo_doc, "doctype", None) == "Acordo de Honorarios Processuais":
		return acordo_doc
	return None


def _ensure_parcela_origem_ids(acordo):
	for parcela in acordo.get("parcelas") or []:
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
		"tipo_origem": TIPO_HONORARIOS,
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
	if is_pagamento_atos(pagamento):
		return False
	if pagamento.status == "Cancelado":
		return False
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
		"tipo_origem",
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
	if is_pagamento_atos(pagamento):
		return
	if pagamento.status == "Cancelado":
		return
	new_status = STATUS_PARCELA_TO_PAGAMENTO.get(parcela.status or "Pendente", "Pendente")
	if pagamento.status != new_status and pagamento.status in ("Pendente", "Vencido"):
		pagamento.status = new_status
		pagamento.sincronizado_em = now_datetime()
		pagamento.save(ignore_permissions=True)


def _cancelar_pagamentos_orfaos(acordo_name, active_origem_ids):
	cancelados = 0
	filters = {
		"acordo": acordo_name,
		"tipo_origem": ["in", [TIPO_HONORARIOS, ""]],
	}
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
