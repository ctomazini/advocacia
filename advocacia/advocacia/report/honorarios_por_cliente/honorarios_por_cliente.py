# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{
			"fieldname": "cliente",
			"label": _("Cliente"),
			"fieldtype": "Link",
			"options": "Cliente",
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
			"fieldname": "total_pendente",
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
			"label": _("Serviços"),
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
		query_filters["data_vencimento"] = ["between", [de_data, ate_data]]
	elif de_data:
		query_filters["data_vencimento"] = [">=", de_data]
	elif ate_data:
		query_filters["data_vencimento"] = ["<=", ate_data]

	if filters.get("cliente"):
		query_filters["cliente"] = filters.cliente

	pagamentos = frappe.get_all(
		"Pagamento",
		filters=query_filters,
		fields=["cliente", "acordo", "servico", "valor", "valor_recebido", "status"],
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
		grouped[row.cliente].append(row)

	rows = []
	sum_contratado = sum_recebido = sum_pendente = sum_vencido = 0.0

	for cliente, items in grouped.items():
		total_contratado = sum(flt(p.valor) for p in items)
		total_recebido = sum(
			flt(p.valor_recebido or p.valor)
			for p in items
			if p.status in ("Recebido", "Repassado")
		)
		total_pendente = sum(flt(p.valor) for p in items if p.status == "Pendente")
		total_vencido = sum(flt(p.valor) for p in items if p.status == "Vencido")
		pct = (total_recebido / total_contratado * 100) if total_contratado else 0

		rows.append(
			{
				"cliente": cliente,
				"total_contratado": total_contratado,
				"total_recebido": total_recebido,
				"total_pendente": total_pendente,
				"total_vencido": total_vencido,
				"pct_recebido": pct,
				"qtd_acordos": len({p.acordo for p in items if p.acordo}),
				"qtd_servicos": len({p.servico for p in items if p.servico}),
			}
		)
		sum_contratado += total_contratado
		sum_recebido += total_recebido
		sum_pendente += total_pendente
		sum_vencido += total_vencido

	rows.sort(key=lambda r: flt(r["total_contratado"]), reverse=True)

	chart = {
		"data": {
			"labels": [_("Recebido"), _("Pendente"), _("Vencido")],
			"datasets": [{"values": [sum_recebido, sum_pendente, sum_vencido]}],
		},
		"type": "donut",
		"colors": ["#22c55e", "#3b82f6", "#dc2626"],
	}

	report_summary = [
		{
			"value": sum_contratado,
			"label": _("Contratado"),
			"datatype": "Currency",
			"indicator": "Blue",
		},
		{
			"value": sum_recebido,
			"label": _("Recebido"),
			"datatype": "Currency",
			"indicator": "Green",
		},
		{
			"value": sum_pendente,
			"label": _("Pendente"),
			"datatype": "Currency",
			"indicator": "Orange",
		},
		{
			"value": sum_vencido,
			"label": _("Vencido"),
			"datatype": "Currency",
			"indicator": "Red",
		},
	]

	return rows, chart, report_summary
