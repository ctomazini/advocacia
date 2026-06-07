import frappe
from frappe import _


def _app_display_name():
	return frappe.db.get_single_value("System Settings", "app_name") or "Advocacia"


def notificar_prazos_diario():
	hoje = frappe.utils.today()

	prazos = frappe.get_all(
		"Deadline",
		filters={"status": "Pendente"},
		fields=[
			"name",
			"legal_case",
			"client",
			"data_prazo",
			"descricao",
			"prioridade",
			"responsavel",
			"dias_notificacao",
		],
		limit_page_length=500,
	)

	prazos_urgentes = []

	for prazo in prazos:
		if not prazo.data_prazo:
			continue
		dias_restantes = frappe.utils.date_diff(prazo.data_prazo, hoje)
		dias_notif = prazo.dias_notificacao or 3
		if dias_restantes <= dias_notif:
			prazo["dias_restantes"] = dias_restantes
			prazos_urgentes.append(prazo)

	if not prazos_urgentes:
		return

	vencidos = []
	proximos = []

	for p in sorted(prazos_urgentes, key=lambda x: x["dias_restantes"]):
		if p["dias_restantes"] < 0:
			vencidos.append(p)
		else:
			proximos.append(p)

	html = "<h3>{0} - {1}</h3>".format(
		_("Notificacao de Prazos"),
		frappe.utils.escape_html(_app_display_name()),
	)

	if vencidos:
		html += "<h4 style='color:red'>{0}</h4><ul>".format(_("Prazos Vencidos"))
		for p in vencidos:
			html += "<li><b>{0}</b> - venceu ha {1} dia(s) - Legal Case: {2} - Client: {3}</li>".format(
				p.descricao or p.name,
				abs(p["dias_restantes"]),
				p.legal_case or "N/A",
				p.client or "N/A",
			)
		html += "</ul>"

	if proximos:
		html += "<h4 style='color:orange'>{0}</h4><ul>".format(_("Prazos Proximos"))
		for p in proximos:
			if p["dias_restantes"] == 0:
				label = "HOJE"
			elif p["dias_restantes"] == 1:
				label = "AMANHA"
			else:
				label = "em {0} dias".format(p["dias_restantes"])
			html += "<li><b>{0}</b> - vence {1} ({2}) - Legal Case: {3} - Client: {4}</li>".format(
				p.descricao or p.name,
				label,
				frappe.utils.formatdate(p.data_prazo, "dd/MM/yyyy"),
				p.legal_case or "N/A",
				p.client or "N/A",
			)
		html += "</ul>"

	html += "<p><a href='{0}/app/controle-de-prazos?status=Pendente'>{1}</a></p>".format(
		frappe.utils.get_url(),
		_("Ver todos os prazos pendentes"),
	)

	users = frappe.get_all(
		"Has Role",
		filters={"role": "Advocacia Manager", "parenttype": "User"},
		fields=["parent"],
	)
	recipients = list({u.parent for u in users if u.parent != "Administrator"})

	if not recipients:
		recipients = [frappe.db.get_value("User", "Administrator", "email")]

	if recipients:
		frappe.sendmail(
			recipients=recipients,
			subject="[Advocacia] {0} prazo(s) urgente(s)".format(len(prazos_urgentes)),
			message=html,
			now=True,
		)
