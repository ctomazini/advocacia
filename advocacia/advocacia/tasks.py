import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import add_days, getdate, today


def verificar_parcelas_vencidas():
	"""Marca pagamentos/parcelas pendentes com vencimento anterior a hoje como vencidos."""
	hoje = today()
	from advocacia.advocacia.financeiro import sync_parcela_from_pagamento

	pagamentos = frappe.get_all(
		"Legal Payment",
		filters={"data_vencimento": ["<", hoje], "status": "Pendente", "manual_override": 0},
		fields=["name", "parcela_origem_id"],
		limit_page_length=0,  # processa todos — scheduler batch
	)
	for row in pagamentos:
		frappe.db.set_value("Legal Payment", row.name, "status", "Vencido", update_modified=False)
		pag = frappe.get_doc("Legal Payment", row.name)
		sync_parcela_from_pagamento(pag)

	parcelas = frappe.get_all(
		"Fee Installment",
		filters={"vencimento": ["<", hoje], "status": "Pendente"},
		pluck="name",
		limit_page_length=0,  # processa todos — scheduler batch
	)
	for name in parcelas:
		frappe.db.set_value("Fee Installment", name, "status", "Vencido", update_modified=False)

	frappe.logger().info(
		"Vencidos atualizados: {0} pagamentos, {1} parcelas".format(len(pagamentos), len(parcelas))
	)


def verificar_despesas_vencidas():
	"""Marca despesas pendentes como atrasadas se vencimento passou."""
	despesas = frappe.get_all(
		"Office Expense",
		filters={"status": "Pendente", "data_vencimento": ("<", today())},
		pluck="name",
		limit_page_length=0,  # processa todos — scheduler batch
	)
	for name in despesas:
		frappe.db.set_value("Office Expense", name, "status", "Atrasado", update_modified=False)

	if despesas:
		frappe.logger().info("Despesas marcadas como atrasadas: {0}".format(len(despesas)))


def notificar_parcelas_vencidas():
	"""Notifica pagamentos vencidos ha 3 dias (camada operacional)."""
	data_alvo = add_days(today(), -3)
	pagamentos = frappe.get_all(
		"Legal Payment",
		filters={"status": "Vencido", "data_vencimento": data_alvo},
		fields=["name", "fee_agreement", "client", "data_vencimento", "owner", "tipo_origem", "service_record"],
		limit_page_length=500,
	)
	count = 0
	for p in pagamentos:
		subject = _("Legal Payment vencido: {0}").format(p.name)
		if _notification_already_sent("Legal Payment", p.name, subject):
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
			doctype="Legal Payment",
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
		"Hearing",
		filters={"data_hora": ["between", [hoje + " 00:00:00", hoje + " 23:59:59"]]},
		fields=[
			"name",
			"client",
			"tipo",
			"modalidade",
			"data_hora",
			"court_branch",
			"owner",
		],
		limit_page_length=500,
	)
	count = 0
	for aud in audiencias:
		subject = _("Hearing hoje: {0} - {1}").format(
			aud.client or aud.name,
			aud.tipo or "",
		)
		if _notification_already_sent("Hearing", aud.name, subject):
			continue
		message = _(
			"Hearing {0} ({1}) hoje as {2}. Court Branch: {3}."
		).format(
			aud.tipo or "",
			aud.modalidade or "",
			frappe.utils.format_datetime(aud.data_hora) if aud.data_hora else "",
			aud.court_branch or _("N/A"),
		)
		_send_system_notification(
			users=[aud.owner] if aud.owner else [],
			doctype="Hearing",
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
	if doc.parenttype != "Fee Agreement" or not doc.parent:
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
	if not doc.fee_agreement:
		return
	_marcar_acordo_quitado_se_completo(doc.fee_agreement, usar_pagamentos=True)


def _marcar_acordo_quitado_se_completo(acordo_name, usar_pagamentos=False):
	if usar_pagamentos:
		pagamentos = frappe.get_all(
			"Legal Payment",
			filters={"fee_agreement": acordo_name, "status": ["not in", ["Cancelado"]]},
			fields=["status"],
			limit_page_length=500,
		)
		if not pagamentos or not all(p.status in ("Recebido", "Repassado") for p in pagamentos):
			return
	else:
		parcelas = frappe.get_all(
			"Fee Installment",
			filters={
				"parent": acordo_name,
				"parenttype": "Fee Agreement",
			},
			fields=["status"],
			limit_page_length=500,
		)
		if not parcelas or not all(p.status == "Recebido" for p in parcelas):
			return

	acordo_status = frappe.db.get_value("Fee Agreement", acordo_name, "status")
	if acordo_status == "Quitado":
		return

	frappe.db.set_value(
		"Fee Agreement",
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
	if pagamento.fee_agreement:
		acordo_owner = frappe.db.get_value(
			"Fee Agreement", pagamento.fee_agreement, "owner"
		)
		if acordo_owner and acordo_owner not in users:
			users.append(acordo_owner)
	elif getattr(pagamento, "service_record", None):
		registro_owner = frappe.db.get_value(
			"Service Record", pagamento.service_record, "owner"
		)
		if registro_owner and registro_owner not in users:
			users.append(registro_owner)
	return users or ["Administrator"]


def _pagamento_origem_label(pagamento):
	if pagamento.fee_agreement:
		return pagamento.fee_agreement
	if getattr(pagamento, "service_record", None):
		return _("Atos: {0}").format(pagamento.service_record)
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
		"Legal Case",
		filters={"status": "Em andamento"},
		fields=["name"],
		limit_page_length=0,  # processa todos — scheduler batch
	)
	if not servicos:
		return

	servico_names = [s.name for s in servicos]
	acordos = frappe.get_all(
		"Fee Agreement",
		filters={"legal_case": ["in", servico_names], "status": "Vigente"},
		fields=["name", "legal_case"],
		limit_page_length=0,  # processa todos — scheduler batch
	)
	acordo_names = [ac.name for ac in acordos]
	servicos_com_parcela_aberta = set()

	if acordo_names:
		parcelas_abertas = frappe.get_all(
			"Fee Installment",
			filters={
				"parent": ["in", acordo_names],
				"status": ["in", ["Pendente", "Vencido"]],
			},
			fields=["parent"],
			pluck="parent",
			limit_page_length=0,  # processa todos — scheduler batch
		)
		pagamentos_abertos = frappe.get_all(
			"Legal Payment",
			filters={
				"fee_agreement": ["in", acordo_names],
				"status": ["in", ["Pendente", "Vencido"]],
			},
			fields=["fee_agreement"],
			pluck="fee_agreement",
			limit_page_length=0,  # processa todos — scheduler batch
		)
		acordos_com_pendencia = set(parcelas_abertas) | set(pagamentos_abertos)
		for ac in acordos:
			if ac.name in acordos_com_pendencia:
				servicos_com_parcela_aberta.add(ac.legal_case)

	servicos_com_prazo = set(
		frappe.get_all(
			"Deadline",
			filters={"legal_case": ["in", servico_names], "status": "Pendente"},
			fields=["legal_case"],
			pluck="legal_case",
			limit_page_length=0,  # processa todos — scheduler batch
		)
	)
	servicos_com_audiencia = set(
		frappe.get_all(
			"Hearing",
			filters={
				"legal_case": ["in", servico_names],
				"data_hora": [">=", f"{hoje} 00:00:00"],
			},
			fields=["legal_case"],
			pluck="legal_case",
			limit_page_length=0,  # processa todos — scheduler batch
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

		frappe.db.set_value("Legal Case", nome, "status", "Arquivado")
		frappe.logger().info("Legal Case {0} arquivado automaticamente".format(nome))
