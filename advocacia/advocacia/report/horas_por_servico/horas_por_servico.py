# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not frappe.db.table_exists("Time Entry"):
		return _get_columns(), [], None, _empty_chart(), _empty_summary()

	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{
			"fieldname": "legal_case",
			"label": _("Serviço"),
			"fieldtype": "Link",
			"options": "Legal Case",
			"width": 120,
		},
		{"fieldname": "servico_titulo", "label": _("Título"), "fieldtype": "Data", "width": 200},
		{
			"fieldname": "client",
			"label": _("Cliente"),
			"fieldtype": "Link",
			"options": "Client",
			"width": 160,
		},
		{"fieldname": "area", "label": _("Área"), "fieldtype": "Data", "width": 110},
		{
			"fieldname": "qtd_registros",
			"label": _("Registros"),
			"fieldtype": "Int",
			"width": 90,
		},
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
			"fieldname": "pct_cobravel",
			"label": _("% Cobrável"),
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "valor_honorarios",
			"label": _("Honorários Contratados"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "valor_hora",
			"label": _("Valor/Hora Efetivo"),
			"fieldtype": "Currency",
			"width": 140,
		},
	]


def _period_bounds(filters):
	hoje = getdate(today())
	periodo = filters.get("periodo") or "Últimos 6 Meses"
	if periodo == "Tudo":
		return None, None
	if periodo == "Personalizado":
		de_data = getdate(filters.de_data) if filters.get("de_data") else None
		ate_data = getdate(filters.ate_data) if filters.get("ate_data") else hoje
		return de_data, ate_data
	if periodo == "Último Mês":
		return add_months(hoje, -1), hoje
	if periodo == "Últimos 3 Meses":
		return add_months(hoje, -3), hoje
	if periodo == "Últimos 6 Meses":
		return add_months(hoje, -6), hoje
	if periodo == "Último Ano":
		return add_months(hoje, -12), hoje
	return add_months(hoje, -6), hoje


def _get_data(filters):
	period_start, period_end = _period_bounds(filters)
	query_filters = {}
	if filters.get("legal_case"):
		query_filters["legal_case"] = filters.legal_case
	if filters.get("client"):
		query_filters["client"] = filters.client
	if period_start and period_end:
		query_filters["data"] = ["between", [period_start, period_end]]
	elif period_start:
		query_filters["data"] = [">=", period_start]
	elif period_end:
		query_filters["data"] = ["<=", period_end]

	registros = frappe.get_all(
		"Time Entry",
		filters=query_filters,
		fields=["legal_case", "client", "duracao_horas", "cobravel"],
		limit_page_length=0,
	)

	by_servico = defaultdict(
		lambda: {
			"client": "",
			"total": 0.0,
			"cobravel": 0.0,
			"nao_cobravel": 0.0,
			"qtd_registros": 0,
		}
	)

	for r in registros:
		if not r.legal_case:
			continue
		b = by_servico[r.legal_case]
		b["client"] = r.client or b["client"]
		b["qtd_registros"] += 1
		h = flt(r.duracao_horas)
		b["total"] += h
		if r.cobravel:
			b["cobravel"] += h
		else:
			b["nao_cobravel"] += h

	if filters.get("area"):
		filtered = {}
		for servico, stats in by_servico.items():
			area = frappe.db.get_value("Legal Case", servico, "area") or ""
			if area == filters.area:
				filtered[servico] = stats
		by_servico = filtered

	honorarios = {}
	for row in frappe.get_all(
		"Fee Agreement",
		fields=["legal_case", "valor_total_do_acordo"],
		limit_page_length=0,
	):
		if row.legal_case:
			honorarios[row.legal_case] = honorarios.get(row.legal_case, 0) + flt(row.valor_total_do_acordo)

	rows = []
	sum_total = sum_cobravel = sum_nao_cobravel = sum_honorarios = 0.0
	sum_registros = 0

	for servico, stats in by_servico.items():
		servico_doc = frappe.db.get_value(
			"Legal Case", servico, ["title", "area"], as_dict=True
		) or {}
		area = servico_doc.get("area") or ""
		titulo = servico_doc.get("title") or servico
		valor_hon = honorarios.get(servico, 0)
		valor_hora = valor_hon / stats["total"] if stats["total"] else 0
		pct_cobravel = (stats["cobravel"] / stats["total"] * 100) if stats["total"] else 0

		rows.append(
			{
				"legal_case": servico,
				"servico_titulo": titulo,
				"client": stats["client"],
				"area": area,
				"qtd_registros": stats["qtd_registros"],
				"total_horas": round(stats["total"], 2),
				"horas_cobraveis": round(stats["cobravel"], 2),
				"horas_nao_cobraveis": round(stats["nao_cobravel"], 2),
				"pct_cobravel": pct_cobravel,
				"valor_honorarios": valor_hon,
				"valor_hora": valor_hora,
			}
		)
		sum_total += stats["total"]
		sum_cobravel += stats["cobravel"]
		sum_nao_cobravel += stats["nao_cobravel"]
		sum_honorarios += valor_hon
		sum_registros += stats["qtd_registros"]

	rows.sort(key=lambda r: flt(r["total_horas"]), reverse=True)

	if rows:
		rows.append({})
		rows.append(
			{
				"legal_case": "",
				"servico_titulo": _("Total"),
				"client": "",
				"area": "",
				"qtd_registros": sum_registros,
				"total_horas": round(sum_total, 2),
				"horas_cobraveis": round(sum_cobravel, 2),
				"horas_nao_cobraveis": round(sum_nao_cobravel, 2),
				"pct_cobravel": (sum_cobravel / sum_total * 100) if sum_total else 0,
				"valor_honorarios": sum_honorarios,
				"valor_hora": sum_honorarios / sum_total if sum_total else 0,
			}
		)

	chart_labels = []
	cobraveis_chart = []
	nao_cobraveis_chart = []
	for row in rows:
		if not row.get("legal_case"):
			continue
		label = row.get("servico_titulo") or row["legal_case"]
		if len(label) > 28:
			label = label[:25] + "..."
		chart_labels.append(label)
		cobraveis_chart.append(flt(row.get("horas_cobraveis")))
		nao_cobraveis_chart.append(flt(row.get("horas_nao_cobraveis")))
		if len(chart_labels) >= 10:
			break

	chart = None
	if chart_labels:
		chart = {
			"data": {
				"labels": chart_labels,
				"datasets": [
					{"name": _("Cobráveis"), "values": cobraveis_chart},
					{"name": _("Não cobráveis"), "values": nao_cobraveis_chart},
				],
			},
			"type": "bar",
			"colors": ["#22c55e", "#94a3b8"],
		}

	pct_geral = (sum_cobravel / sum_total * 100) if sum_total else 0
	report_summary = [
		{
			"value": round(sum_total, 2),
			"label": _("Total Horas"),
			"datatype": "Float",
			"indicator": "Blue",
		},
		{
			"value": round(sum_cobravel, 2),
			"label": _("Horas Cobráveis"),
			"datatype": "Float",
			"indicator": "Green",
		},
		{
			"value": pct_geral,
			"label": _("% Cobrável"),
			"datatype": "Percent",
			"indicator": "Green" if pct_geral >= 70 else "Orange",
		},
		{
			"value": len(by_servico),
			"label": _("Serviços c/ horas"),
			"datatype": "Int",
			"indicator": "Blue",
		},
		{
			"value": sum_honorarios / sum_total if sum_total else 0,
			"label": _("Valor/Hora Médio"),
			"datatype": "Currency",
			"indicator": "Blue",
		},
	]

	return rows, chart, report_summary


def _empty_chart():
	return {
		"data": {"labels": [], "datasets": [{"name": _("Cobráveis"), "values": []}]},
		"type": "bar",
	}


def _empty_summary():
	return [
		{"value": 0, "label": _("Total Horas"), "datatype": "Float", "indicator": "Blue"},
	]
