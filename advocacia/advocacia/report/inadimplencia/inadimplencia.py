# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, today

from advocacia.advocacia.report_visuals import REPORT_COLORS, bar_chart, currency_summary, int_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{
			"fieldname": "client",
			"label": _("Cliente"),
			"fieldtype": "Link",
			"options": "Client",
			"width": 180,
		},
		{
			"fieldname": "total_vencido",
			"label": _("Total Vencido (R$)"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "qtd_parcelas",
			"label": _("Parcelas"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "dias_atraso_max",
			"label": _("Maior Atraso"),
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"fieldname": "dias_atraso_medio",
			"label": _("Atraso Médio"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "contato_tel",
			"label": _("Telefone"),
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"fieldname": "contato_email",
			"label": _("E-mail"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "servicos",
			"label": _("Serviços"),
			"fieldtype": "Small Text",
			"width": 250,
		},
	]


def _get_data(filters):
	hoje = getdate(today())
	de_data = getdate(filters.de_data) if filters.get("de_data") else None
	ate_data = getdate(filters.ate_data) if filters.get("ate_data") else hoje

	query_filters = {
		"status": "Vencido",
		"data_vencimento": ["between", [de_data, ate_data]] if de_data else ["<=", ate_data],
	}
	if filters.get("client"):
		query_filters["client"] = filters.client

	pagamentos = frappe.get_all(
		"Legal Payment",
		filters=query_filters,
		fields=["client", "legal_case", "valor", "data_vencimento"],
		limit_page_length=0,
	)

	grouped = defaultdict(list)
	for row in pagamentos:
		grouped[row.client].append(row)

	rows = []
	total_geral = 0.0
	total_parcelas = 0
	soma_atraso = 0

	for cliente, items in grouped.items():
		dias_list = [max(date_diff(hoje, getdate(p.data_vencimento)), 0) for p in items]
		total_vencido = sum(flt(p.valor) for p in items)
		tel, email = _get_cliente_contato(cliente)
		servicos = _format_servicos({p.legal_case for p in items if p.legal_case})

		rows.append(
			{
				"client": cliente,
				"total_vencido": total_vencido,
				"qtd_parcelas": len(items),
				"dias_atraso_max": max(dias_list) if dias_list else 0,
				"dias_atraso_medio": round(sum(dias_list) / len(dias_list), 1) if dias_list else 0,
				"contato_tel": tel,
				"contato_email": email,
				"servicos": servicos,
			}
		)
		total_geral += total_vencido
		total_parcelas += len(items)
		soma_atraso += sum(dias_list)

	rows.sort(key=lambda r: flt(r["total_vencido"]), reverse=True)

	chart_labels = []
	chart_values = []
	for row in rows[:10]:
		chart_labels.append(frappe.db.get_value("Client", row["client"], "nome") or row["client"])
		chart_values.append(flt(row["total_vencido"]))

	chart = bar_chart(
		chart_labels,
		[{"name": _("Vencido (R$)"), "values": chart_values}],
		[REPORT_COLORS["red"]],
	)

	media_atraso = round(soma_atraso / total_parcelas, 1) if total_parcelas else 0
	report_summary = [
		currency_summary(total_geral, _("Total Vencido"), "Red"),
		int_summary(total_parcelas, _("Parcelas Vencidas"), "Red"),
		{
			"value": media_atraso,
			"label": _("Atraso Médio (dias)"),
			"datatype": "Float",
			"indicator": "Orange",
		},
	]

	return rows, chart, report_summary


def _get_cliente_contato(cliente):
	contatos = frappe.get_all(
		"Client Contact",
		filters={"parent": cliente, "parenttype": "Client"},
		fields=["celular", "telefone", "email"],
		order_by="idx asc",
	)
	tel = ""
	email = ""
	for c in contatos:
		if not tel:
			tel = c.celular or c.telefone or ""
		if not email and c.email:
			email = c.email
		if tel and email:
			break
	return tel, email


def _format_servicos(servico_ids):
	labels = []
	for sid in sorted(servico_ids):
		title = frappe.db.get_value("Legal Case", sid, "title") or sid
		labels.append(title)
	return ", ".join(labels)
