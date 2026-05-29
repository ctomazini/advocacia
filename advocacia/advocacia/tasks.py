import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import add_days, getdate, today


def verificar_parcelas_vencidas():
	"""Marca parcelas pendentes com vencimento anterior a hoje como Vencida."""
	hoje = today()
	parcelas = frappe.get_all(
		"Parcela de Honorarios",
		filters={"vencimento": ["<", hoje], "status": "Pendente"},
		pluck="name",
	)
	for name in parcelas:
		frappe.db.set_value("Parcela de Honorarios", name, "status", "Vencida", update_modified=False)

	count = len(parcelas)
	frappe.logger().info("Parcelas vencidas atualizadas: {0}".format(count))
	frappe.db.commit()


def notificar_parcelas_vencidas():
	"""Notifica parcelas vencidas ha 3 dias (status Vencida, vencimento = hoje - 3)."""
	data_alvo = add_days(today(), -3)
	parcelas = frappe.get_all(
		"Parcela de Honorarios",
		filters={"status": "Vencida", "vencimento": data_alvo},
		fields=["name", "parent", "parenttype", "vencimento", "owner"],
	)
	count = 0
	for p in parcelas:
		subject = _("Parcela vencida: {0}").format(p.name)
		if _notification_already_sent("Parcela de Honorarios", p.name, subject):
			continue
		message = _(
			"A parcela {0} (vencimento {1}) esta vencida ha 3 dias. Acordo: {2}."
		).format(
			p.name,
			frappe.utils.formatdate(p.vencimento),
			p.parent or _("N/A"),
		)
		_send_system_notification(
			users=_parcela_recipients(p),
			doctype="Parcela de Honorarios",
			docname=p.name,
			subject=subject,
			message=message,
		)
		count += 1

	frappe.logger().info("Notificacoes de parcelas vencidas enviadas: {0}".format(count))
	frappe.db.commit()


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
	frappe.db.commit()


def on_parcela_update(doc, method=None):
	"""Quando todas as parcelas do acordo estao Recebida, marca o acordo como Quitado."""
	if doc.status != "Recebida":
		return
	if doc.parenttype != "Acordo de Honorarios Processuais" or not doc.parent:
		return

	parcelas = frappe.get_all(
		"Parcela de Honorarios",
		filters={
			"parent": doc.parent,
			"parenttype": "Acordo de Honorarios Processuais",
		},
		fields=["status"],
	)
	if not parcelas or not all(p.status == "Recebida" for p in parcelas):
		return

	acordo = frappe.get_doc("Acordo de Honorarios Processuais", doc.parent)
	if acordo.status == "Quitado":
		return

	acordo.status = "Quitado"
	acordo.save(ignore_permissions=True)
	frappe.logger().info("Acordo {0} quitado".format(doc.parent))


def _parcela_recipients(parcela):
	users = []
	if parcela.owner:
		users.append(parcela.owner)
	if parcela.parenttype == "Acordo de Honorarios Processuais" and parcela.parent:
		acordo_owner = frappe.db.get_value(
			"Acordo de Honorarios Processuais", parcela.parent, "owner"
		)
		if acordo_owner and acordo_owner not in users:
			users.append(acordo_owner)
	return users or ["Administrator"]


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

	for s in servicos:
		nome = s.name

		acordos = frappe.get_all(
			"Acordo de Honorarios Processuais",
			filters={"servico": nome, "status": ["in", ["Vigente"]]},
			fields=["name"],
		)
		tem_parcela_aberta = False
		for ac in acordos:
			count = frappe.db.count(
				"Parcela de Honorarios",
				{"parent": ac.name, "status": ["in", ["Pendente", "Vencida"]]},
			)
			if count > 0:
				tem_parcela_aberta = True
				break

		if tem_parcela_aberta:
			continue

		tem_prazo = frappe.db.count(
			"Controle de Prazos",
			{"servico": nome, "status": "Pendente"},
		)
		if tem_prazo:
			continue

		tem_audiencia = frappe.db.count(
			"Audiencia",
			{"servico": nome, "data_hora": [">=", f"{hoje} 00:00:00"]},
		)
		if tem_audiencia:
			continue

		frappe.db.set_value("Servico", nome, "status", "Arquivado")
		frappe.logger().info("Servico {0} arquivado automaticamente".format(nome))

	frappe.db.commit()
