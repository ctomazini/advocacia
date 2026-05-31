# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not frappe.db.table_exists("Registro de Horas"):
		return _get_columns(), []

	columns = _get_columns()
	data = _get_data(filters)
	return columns, data


def _get_columns():
	return [
		{
			"fieldname": "servico",
			"label": _("Serviço"),
			"fieldtype": "Link",
			"options": "Servico",
			"width": 120,
		},
		{
			"fieldname": "cliente",
			"label": _("Cliente"),
			"fieldtype": "Link",
			"options": "Cliente",
			"width": 160,
		},
		{"fieldname": "area", "label": _("Área"), "fieldtype": "Data", "width": 120},
		{
			"fieldname": "total_horas",
			"label": _("Total Horas"),
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"fieldname": "horas_cobraveis",
			"label": _("Horas Cobráveis"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "horas_nao_cobraveis",
			"label": _("Horas Não-Cobráveis"),
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"fieldname": "valor_honorarios",
			"label": _("Valor Honorários"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "valor_hora",
			"label": _("Valor/Hora"),
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def _get_data(filters):
	query_filters = {}
	if filters.get("servico"):
		query_filters["servico"] = filters.servico
	if filters.get("cliente"):
		query_filters["cliente"] = filters.cliente

	registros = frappe.get_all(
		"Registro de Horas",
		filters=query_filters,
		fields=["servico", "cliente", "duracao_horas", "cobravel"],
		limit_page_length=0,
	)

	by_servico = defaultdict(
		lambda: {
			"cliente": "",
			"total": 0.0,
			"cobravel": 0.0,
			"nao_cobravel": 0.0,
		}
	)

	for r in registros:
		if not r.servico:
			continue
		b = by_servico[r.servico]
		b["cliente"] = r.cliente or b["cliente"]
		h = flt(r.duracao_horas)
		b["total"] += h
		if r.cobravel:
			b["cobravel"] += h
		else:
			b["nao_cobravel"] += h

	honorarios = {}
	for row in frappe.get_all(
		"Acordo de Honorarios Processuais",
		fields=["servico", "valor_total_do_acordo"],
		limit_page_length=0,
	):
		if row.servico:
			honorarios[row.servico] = honorarios.get(row.servico, 0) + flt(row.valor_total_do_acordo)

	rows = []
	for servico, stats in sorted(by_servico.items()):
		area = frappe.db.get_value("Servico", servico, "area") or ""
		valor_hon = honorarios.get(servico, 0)
		valor_hora = valor_hon / stats["total"] if stats["total"] else 0
		rows.append(
			{
				"servico": servico,
				"cliente": stats["cliente"],
				"area": area,
				"total_horas": round(stats["total"], 2),
				"horas_cobraveis": round(stats["cobravel"], 2),
				"horas_nao_cobraveis": round(stats["nao_cobravel"], 2),
				"valor_honorarios": valor_hon,
				"valor_hora": valor_hora,
			}
		)

	return rows
