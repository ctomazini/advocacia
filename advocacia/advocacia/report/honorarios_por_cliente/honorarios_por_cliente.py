# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, getdate

from advocacia.advocacia.report_visuals import HONORARIOS_CHART_COLORS, currency_summary, donut_chart


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
			"fieldname": "total_contratado",
			"label": _("Contratado (R$)"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "total_recebido",
			"label": _("Recebido (R$)"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "pending_total",
			"label": _("Pendente (R$)"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "total_vencido",
			"label": _("Vencido (R$)"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "pct_recebido",
			"label": _("% Recebido"),
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "qtd_acordos",
			"label": _("Acordos"),
			"fieldtype": "Int",
			"width": 80,
		},
		{
			"fieldname": "qtd_servicos",
			"label": _("Processos"),
			"fieldtype": "Int",
			"width": 80,
		},
	]


def _get_data(filters):
	de_data = getdate(filters.de_data) if filters.get("de_data") else None
	ate_data = getdate(filters.ate_data) if filters.get("ate_data") else None

	query_filters = {
		"status": ["!=", "Cancelado"],
	}
	if de_data and ate_data:
		query_filters["due_date"] = ["between", [de_data, ate_data]]
	elif de_data:
		query_filters["due_date"] = [">=", de_data]
	elif ate_data:
		query_filters["due_date"] = ["<=", ate_data]

	if filters.get("client"):
		query_filters["client"] = filters.client

	pagamentos = frappe.get_all(
		"Legal Payment",
		filters=query_filters,
		fields=["client", "fee_agreement", "legal_case", "amount", "received_amount", "status"],
		limit_page_length=0,
	)

	if filters.get("status_filtro"):
		status_map = {
			"Pendente": "Pendente",
			"Vencido": "Vencido",
			"Recebido": ("Recebido", "Repassado"),
		}
		want = status_map.get(filters.status_filtro)
		if want:
			if isinstance(want, tuple):
				pagamentos = [p for p in pagamentos if p.status in want]
			else:
				pagamentos = [p for p in pagamentos if p.status == want]

	grouped = defaultdict(list)
	for row in pagamentos:
		grouped[row.client].append(row)

	rows = []
	sum_contratado = sum_recebido = sum_pendente = sum_vencido = 0.0

	for cliente, items in grouped.items():
		total_contratado = sum(flt(p.amount) for p in items)
		total_recebido = sum(
			flt(p.received_amount or p.amount)
			for p in items
			if p.status in ("Recebido", "Repassado")
		)
		total_pendente = sum(flt(p.amount) for p in items if p.status == "Pendente")
		total_vencido = sum(flt(p.amount) for p in items if p.status == "Vencido")
		pct = (total_recebido / total_contratado * 100) if total_contratado else 0

		rows.append(
			{
				"client": cliente,
				"total_contratado": total_contratado,
				"total_recebido": total_recebido,
				"pending_total": total_pendente,
				"total_vencido": total_vencido,
				"pct_recebido": pct,
				"qtd_acordos": len({p.fee_agreement for p in items if p.fee_agreement}),
				"qtd_servicos": len({p.legal_case for p in items if p.legal_case}),
			}
		)
		sum_contratado += total_contratado
		sum_recebido += total_recebido
		sum_pendente += total_pendente
		sum_vencido += total_vencido

	rows.sort(key=lambda r: flt(r["total_contratado"]), reverse=True)

	chart = donut_chart(
		[_("Recebido"), _("Pendente"), _("Vencido")],
		[sum_recebido, sum_pendente, sum_vencido],
		HONORARIOS_CHART_COLORS,
	)

	report_summary = [
		currency_summary(sum_contratado, _("Contratado"), "Blue"),
		currency_summary(sum_recebido, _("Recebido"), "Green"),
		currency_summary(sum_pendente, _("Pendente"), "Orange"),
		currency_summary(sum_vencido, _("Vencido"), "Red"),
	]

	return rows, chart, report_summary
