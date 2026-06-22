# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import add_months, cint, date_diff, flt, getdate, today

from advocacia.advocacia.report_visuals import PRODUCTIVITY_CHART_COLORS, bar_chart, currency_summary, int_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "area", "label": _("Área Jurídica"), "fieldtype": "Data", "width": 140},
		{"fieldname": "total_servicos", "label": _("Total de Processos"), "fieldtype": "Int", "width": 110},
		{"fieldname": "em_andamento", "label": _("Em Andamento"), "fieldtype": "Int", "width": 110},
		{"fieldname": "encerrados", "label": _("Encerrados"), "fieldtype": "Int", "width": 100},
		{
			"fieldname": "taxa_encerramento",
			"label": _("Taxa de Encerramento (%)"),
			"fieldtype": "Percent",
			"width": 150,
		},
		{
			"fieldname": "tempo_medio_dias",
			"label": _("Tempo Médio (dias)"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "total_honorarios",
			"label": _("Total Honorários"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "total_custas",
			"label": _("Total Custas"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "lucro_liquido",
			"label": _("Lucro Líquido por Área"),
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"fieldname": "horas_registradas",
			"label": _("Horas Registradas"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "valor_hora_efetivo",
			"label": _("Valor/Hora Efetivo"),
			"fieldtype": "Currency",
			"width": 140,
		},
	]


def _period_start(periodo):
	hoje = getdate(today())
	if periodo == "Último Mês":
		return add_months(hoje, -1)
	if periodo == "Últimos 3 Meses":
		return add_months(hoje, -3)
	if periodo == "Últimos 6 Meses":
		return add_months(hoje, -6)
	if periodo == "Último Ano":
		return add_months(hoje, -12)
	return None


def _get_data(filters):
	period_start = _period_start(filters.get("periodo") or "Últimos 6 Meses")
	servico_filters = {}
	if filters.get("area"):
		servico_filters["area"] = filters.area

	servicos = frappe.get_all(
		"Legal Case",
		filters=servico_filters,
		fields=["name", "area", "status", "opening_date", "modified"],
		limit_page_length=0,
	)

	if period_start:
		servicos = [
			s
			for s in servicos
			if s.opening_date and getdate(s.opening_date) >= getdate(period_start)
		]

	by_area = defaultdict(
		lambda: {
			"total": 0,
			"em_andamento": 0,
			"encerrados": 0,
			"dias_encerramento": [],
			"servico_names": [],
		}
	)

	for s in servicos:
		area = s.area or _("Sem área")
		bucket = by_area[area]
		bucket["total"] += 1
		bucket["servico_names"].append(s.name)
		if s.status == "Em andamento":
			bucket["em_andamento"] += 1
		elif s.status == "Encerrado":
			bucket["encerrados"] += 1
			if s.opening_date:
				bucket["dias_encerramento"].append(
					date_diff(getdate(s.modified), getdate(s.opening_date))
				)

	honorarios = _sum_honorarios_by_servico()
	custas = _sum_custas_by_servico()
	horas = _sum_horas_by_servico() if cint(filters.get("incluir_horas", 1)) else {}

	rows = []
	chart_labels = []
	honorarios_chart = []
	custas_chart = []
	sum_servicos = sum_honorarios = sum_custas = sum_lucro = sum_horas = 0
	sum_em_andamento = sum_encerrados = 0

	for area, stats in sorted(by_area.items()):
		total = stats["total"]
		enc = stats["encerrados"]
		taxa = (enc / total * 100) if total else 0
		tempo_medio = (
			sum(stats["dias_encerramento"]) / len(stats["dias_encerramento"])
			if stats["dias_encerramento"]
			else 0
		)

		total_hon = sum(honorarios.get(s, 0) for s in stats["servico_names"])
		total_cust = sum(custas.get(s, 0) for s in stats["servico_names"])
		total_horas = sum(horas.get(s, 0) for s in stats["servico_names"])
		lucro = flt(total_hon) - flt(total_cust)
		valor_hora = flt(total_hon) / total_horas if total_horas else 0

		rows.append(
			{
				"area": area,
				"total_servicos": total,
				"em_andamento": stats["em_andamento"],
				"encerrados": enc,
				"taxa_encerramento": taxa,
				"tempo_medio_dias": round(tempo_medio, 1),
				"total_honorarios": total_hon,
				"total_custas": total_cust,
				"lucro_liquido": lucro,
				"horas_registradas": round(total_horas, 2),
				"valor_hora_efetivo": valor_hora,
			}
		)
		chart_labels.append(area)
		honorarios_chart.append(total_hon)
		custas_chart.append(total_cust)
		sum_servicos += total
		sum_em_andamento += stats["em_andamento"]
		sum_encerrados += enc
		sum_honorarios += total_hon
		sum_custas += total_cust
		sum_lucro += lucro
		sum_horas += total_horas

	if rows:
		rows.append({})
		rows.append(
			{
				"area": _("Total"),
				"total_servicos": sum_servicos,
				"em_andamento": sum_em_andamento,
				"encerrados": sum_encerrados,
				"taxa_encerramento": (sum_encerrados / sum_servicos * 100) if sum_servicos else 0,
				"tempo_medio_dias": None,
				"total_honorarios": sum_honorarios,
				"total_custas": sum_custas,
				"lucro_liquido": sum_lucro,
				"horas_registradas": round(sum_horas, 2),
				"valor_hora_efetivo": sum_honorarios / sum_horas if sum_horas else 0,
			}
		)

	chart = None
	if chart_labels:
		chart = bar_chart(
			chart_labels,
			[
				{"name": _("Honorários"), "values": honorarios_chart},
				{"name": _("Custas"), "values": custas_chart},
			],
			PRODUCTIVITY_CHART_COLORS,
		)

	report_summary = [
		int_summary(sum_servicos, _("Processos"), "Blue"),
		currency_summary(sum_honorarios, _("Honorários"), "Green"),
		currency_summary(sum_custas, _("Custas"), "Orange"),
		currency_summary(sum_lucro, _("Lucro Líquido"), "Green" if sum_lucro >= 0 else "Red"),
	]
	if cint(filters.get("incluir_horas", 1)):
		report_summary.append(
			{
				"value": round(sum_horas, 2),
				"label": _("Horas Registradas"),
				"datatype": "Float",
				"indicator": "Blue",
			}
		)

	return rows, chart, report_summary


def _sum_honorarios_by_servico():
	result = defaultdict(float)
	for row in frappe.get_all(
		"Fee Agreement",
		fields=["legal_case", "total_agreement_value"],
		limit_page_length=0,
	):
		if row.legal_case:
			result[row.legal_case] += flt(row.total_agreement_value)
	return result


def _sum_custas_by_servico():
	if not frappe.db.table_exists("Court Cost"):
		return defaultdict(float)
	result = defaultdict(float)
	for row in frappe.get_all(
		"Court Cost",
		filters={"status": ["in", ["Pago", "Repassado"]]},
		fields=["legal_case", "amount"],
		limit_page_length=0,
	):
		if row.legal_case:
			result[row.legal_case] += flt(row.amount)
	return result


def _sum_horas_by_servico():
	if not frappe.db.table_exists("Time Entry"):
		return defaultdict(float)
	result = defaultdict(float)
	for row in frappe.get_all(
		"Time Entry",
		fields=["legal_case", "duration_hours"],
		limit_page_length=0,
	):
		if row.legal_case:
			result[row.legal_case] += flt(row.duration_hours)
	return result
