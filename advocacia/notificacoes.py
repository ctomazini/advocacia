import frappe
from frappe import _


def notificar_prazos_diario():
    hoje = frappe.utils.today()

    prazos = frappe.get_all(
        "Controle de Prazos",
        filters={"status": "Pendente"},
        fields=["name", "servico", "cliente", "data_prazo", "descricao",
                "prioridade", "responsavel", "dias_notificacao"]
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

    html = "<h3>Notificacao de Prazos - Carine Pagel Advocacia</h3>"

    if vencidos:
        html += "<h4 style='color:red'>Prazos Vencidos</h4><ul>"
        for p in vencidos:
            html += "<li><b>{0}</b> - venceu ha {1} dia(s) - Servico: {2} - Cliente: {3}</li>".format(
                p.descricao or p.name,
                abs(p["dias_restantes"]),
                p.servico or "N/A",
                p.cliente or "N/A"
            )
        html += "</ul>"

    if proximos:
        html += "<h4 style='color:orange'>Prazos Proximos</h4><ul>"
        for p in proximos:
            if p["dias_restantes"] == 0:
                label = "HOJE"
            elif p["dias_restantes"] == 1:
                label = "AMANHA"
            else:
                label = "em {0} dias".format(p["dias_restantes"])
            html += "<li><b>{0}</b> - vence {1} ({2}) - Servico: {3} - Cliente: {4}</li>".format(
                p.descricao or p.name,
                label,
                frappe.utils.formatdate(p.data_prazo, "dd/MM/yyyy"),
                p.servico or "N/A",
                p.cliente or "N/A"
            )
        html += "</ul>"

    html += "<p><a href='{0}/app/controle-de-prazos?status=Pendente'>Ver todos os prazos pendentes</a></p>".format(
        frappe.utils.get_url()
    )

    users = frappe.get_all(
        "Has Role",
        filters={"role": "Projects Manager", "parenttype": "User"},
        fields=["parent"]
    )
    recipients = list(set([u.parent for u in users if u.parent != "Administrator"]))

    if not recipients:
        recipients = [frappe.db.get_value("User", "Administrator", "email")]

    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject="[Advocacia] {0} prazo(s) urgente(s)".format(len(prazos_urgentes)),
            message=html,
            now=True
        )


def atualizar_status_faturas():
    """Scheduler diário — atualiza faturas vencidas"""
    from frappe.utils import today
    faturas = frappe.get_all(
        "Fatura",
        filters={
            "status": "Pendente",
            "data_vencimento": ["<", today()],
            "data_pagamento": ["is", "not set"]
        },
        fields=["name"]
    )
    count = 0
    for f in faturas:
        frappe.db.set_value("Fatura", f.name, "status", "Vencida")
        count += 1
    if count:
        frappe.db.commit()
    return count
