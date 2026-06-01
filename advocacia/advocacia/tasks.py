import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import add_days, getdate, today


def verificar_parcelas_vencidas():
	"""Marca pagamentos/parcelas pendentes com vencimento anterior a hoje como vencidos."""
	hoje = today()
	from advocacia.advocacia.financeiro import sync_parcela_from_pagamento

	pagamentos = frappe.get_all(
		"Pagamento",
		filters={"data_vencimento": ["<", hoje], "status": "Pendente", "manual_override": 0},
		fields=["name", "parcela_origem_id"],
	)
	for row in pagamentos:
		frappe.db.set_value("Pagamento", row.name, "status", "Vencido", update_modified=False)
		pag = frappe.get_doc("Pagamento", row.name)
		sync_parcela_from_pagamento(pag)

	parcelas = frappe.get_all(
		"Parcela de Honorarios",
		filters={"vencimento": ["<", hoje], "status": "Pendente"},
		pluck="name",
	)
	for name in parcelas:
		frappe.db.set_value("Parcela de Honorarios", name, "status", "Vencido", update_modified=False)

	frappe.logger().info(
		"Vencidos atualizados: {0} pagamentos, {1} parcelas".format(len(pagamentos), len(parcelas))
	)


def verificar_despesas_vencidas():
	"""Marca despesas pendentes como atrasadas se vencimento passou."""
	despesas = frappe.get_all(
		"Despesa do Escritorio",
		filters={"status": "Pendente", "data_vencimento": ("<", today())},
		pluck="name",
	)
	for name in despesas:
		frappe.db.set_value("Despesa do Escritorio", name, "status", "Atrasado", update_modified=False)

	if despesas:
		frappe.logger().info("Despesas marcadas como atrasadas: {0}".format(len(despesas)))


def notificar_parcelas_vencidas():
	"""Notifica pagamentos vencidos ha 3 dias (camada operacional)."""
	data_alvo = add_days(today(), -3)
	pagamentos = frappe.get_all(
		"Pagamento",
		filters={"status": "Vencido", "data_vencimento": data_alvo},
		fields=["name", "acordo", "cliente", "data_vencimento", "owner", "tipo_origem", "registro_atos"],
	)
	count = 0
	for p in pagamentos:
		subject = _("Pagamento vencido: {0}").format(p.name)
		if _notification_already_sent("Pagamento", p.name, subject):
			continue
		message = _(
			"O pagamento {0} (vencimento {1}) esta vencido ha 3 dias. Origem: {2}."
		).format(
			p.name,
			frappe.utils.formatdate(p.data_vencimento),
			_pagamento_origem_label(p),
		)
		_send_system_notification(
			users=_pagamento_recipients(p),
			doctype="Pagamento",
			docname=p.name,
			subject=subject,
			message=message,
		)
		count += 1

	frappe.logger().info("Notificacoes de pagamentos vencidos enviadas: {0}".format(count))


def notificar_audiencias_hoje():
	"""Notifica o responsavel sobre audiencias agendadas para hoje."""
	hoje = today()
	audiencias = frappe.get_all(
		"Audiencia",
		filters={"data_hora": ["between", [hoje + " 00:00:00", hoje + " 23:59:59"]]},
		fields=[
			"name",
			"cliente",
			"tipo",
			"modalidade",
			"data_hora",
			"local_vara",
			"owner",
		],
	)
	count = 0
	for aud in audiencias:
		subject = _("Audiencia hoje: {0} - {1}").format(
			aud.cliente or aud.name,
			aud.tipo or "",
		)
		if _notification_already_sent("Audiencia", aud.name, subject):
			continue
		message = _(
			"Audiencia {0} ({1}) hoje as {2}. Vara: {3}."
		).format(
			aud.tipo or "",
			aud.modalidade or "",
			frappe.utils.format_datetime(aud.data_hora) if aud.data_hora else "",
			aud.local_vara or _("N/A"),
		)
		_send_system_notification(
			users=[aud.owner] if aud.owner else [],
			doctype="Audiencia",
			docname=aud.name,
			subject=subject,
			message=message,
		)
		count += 1

	frappe.logger().info("Notificacoes de audiencias hoje enviadas: {0}".format(count))


def on_parcela_update(doc, method=None):
	"""Propaga parcela → pagamento e marca acordo quitado quando aplicável."""
	from advocacia.advocacia.financeiro import sync_pagamento_from_parcela

	sync_pagamento_from_parcela(doc)

	if doc.status != "Recebido":
		return
	if doc.parenttype != "Acordo de Honorarios Processuais" or not doc.parent:
		return
	_marcar_acordo_quitado_se_completo(doc.parent)


def on_pagamento_update(doc, method=None):
	"""Propaga status do pagamento para acordo (honorários) ou atos (reversão)."""
	if getattr(frappe.flags, "in_pagamento_sync", False):
		return

	if doc.status == "Cancelado":
		from advocacia.advocacia.financeiro import reverter_atos_do_pagamento

		reverter_atos_do_pagamento(doc)
		return

	if doc.status not in ("Recebido", "Repassado"):
		return
	if not doc.acordo:
		return
	_marcar_acordo_quitado_se_completo(doc.acordo, usar_pagamentos=True)


def _marcar_acordo_quitado_se_completo(acordo_name, usar_pagamentos=False):
	if usar_pagamentos:
		pagamentos = frappe.get_all(
			"Pagamento",
			filters={"acordo": acordo_name, "status": ["not in", ["Cancelado"]]},
			fields=["status"],
		)
		if not pagamentos or not all(p.status in ("Recebido", "Repassado") for p in pagamentos):
			return
	else:
		parcelas = frappe.get_all(
			"Parcela de Honorarios",
			filters={
				"parent": acordo_name,
				"parenttype": "Acordo de Honorarios Processuais",
			},
			fields=["status"],
		)
		if not parcelas or not all(p.status == "Recebido" for p in parcelas):
			return

	acordo_status = frappe.db.get_value("Acordo de Honorarios Processuais", acordo_name, "status")
	if acordo_status == "Quitado":
		return

	frappe.db.set_value(
		"Acordo de Honorarios Processuais",
		acordo_name,
		"status",
		"Quitado",
		update_modified=True,
	)
	frappe.logger().info("Acordo {0} quitado".format(acordo_name))


def _pagamento_recipients(pagamento):
	users = []
	if pagamento.owner:
		users.append(pagamento.owner)
	if pagamento.acordo:
		acordo_owner = frappe.db.get_value(
			"Acordo de Honorarios Processuais", pagamento.acordo, "owner"
		)
		if acordo_owner and acordo_owner not in users:
			users.append(acordo_owner)
	elif getattr(pagamento, "registro_atos", None):
		registro_owner = frappe.db.get_value(
			"Registro de Atos", pagamento.registro_atos, "owner"
		)
		if registro_owner and registro_owner not in users:
			users.append(registro_owner)
	return users or ["Administrator"]


def _pagamento_origem_label(pagamento):
	if pagamento.acordo:
		return pagamento.acordo
	if getattr(pagamento, "registro_atos", None):
		return _("Atos: {0}").format(pagamento.registro_atos)
	return _("N/A")


def _notification_already_sent(document_type, document_name, subject):
	return frappe.db.exists(
		"Notification Log",
		{
			"document_type": document_type,
			"document_name": document_name,
			"subject": subject,
		},
	)


def _send_system_notification(users, doctype, docname, subject, message):
	users = [u for u in users if u]
	if not users:
		users = ["Administrator"]
	enqueue_create_notification(
		users=users,
		doc={
			"type": "Alert",
			"document_type": doctype,
			"document_name": docname,
			"subject": subject,
			"email_content": message,
			"from_user": frappe.session.user or "Administrator",
		},
	)


def verificar_status_servicos():
	"""Verifica servicos Em andamento que podem ser arquivados."""
	hoje = today()

	servicos = frappe.get_all(
		"Servico",
		filters={"status": "Em andamento"},
		fields=["name"],
	)
	if not servicos:
		return

	servico_names = [s.name for s in servicos]
	acordos = frappe.get_all(
		"Acordo de Honorarios Processuais",
		filters={"servico": ["in", servico_names], "status": "Vigente"},
		fields=["name", "servico"],
	)
	acordo_names = [ac.name for ac in acordos]
	servicos_com_parcela_aberta = set()

	if acordo_names:
		parcelas_abertas = frappe.get_all(
			"Parcela de Honorarios",
			filters={
				"parent": ["in", acordo_names],
				"status": ["in", ["Pendente", "Vencido"]],
			},
			fields=["parent"],
			pluck="parent",
		)
		pagamentos_abertos = frappe.get_all(
			"Pagamento",
			filters={
				"acordo": ["in", acordo_names],
				"status": ["in", ["Pendente", "Vencido"]],
			},
			fields=["acordo"],
			pluck="acordo",
		)
		acordos_com_pendencia = set(parcelas_abertas) | set(pagamentos_abertos)
		for ac in acordos:
			if ac.name in acordos_com_pendencia:
				servicos_com_parcela_aberta.add(ac.servico)

	servicos_com_prazo = set(
		frappe.get_all(
			"Controle de Prazos",
			filters={"servico": ["in", servico_names], "status": "Pendente"},
			fields=["servico"],
			pluck="servico",
		)
	)
	servicos_com_audiencia = set(
		frappe.get_all(
			"Audiencia",
			filters={
				"servico": ["in", servico_names],
				"data_hora": [">=", f"{hoje} 00:00:00"],
			},
			fields=["servico"],
			pluck="servico",
		)
	)

	for s in servicos:
		nome = s.name
		if nome in servicos_com_parcela_aberta:
			continue
		if nome in servicos_com_prazo:
			continue
		if nome in servicos_com_audiencia:
			continue

		frappe.db.set_value("Servico", nome, "status", "Arquivado")
		frappe.logger().info("Servico {0} arquivado automaticamente".format(nome))
