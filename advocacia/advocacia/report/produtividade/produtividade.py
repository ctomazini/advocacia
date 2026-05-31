# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import add_months, cint, date_diff, flt, getdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart = _get_data(filters)
	return columns, data, None, chart


def _get_columns():
	return [
		{"fieldname": "area", "label": _("Área Jurídica"), "fieldtype": "Data", "width": 140},
		{"fieldname": "total_servicos", "label": _("Total de Serviços"), "fieldtype": "Int", "width": 110},
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
		"Servico",
		filters=servico_filters,
		fields=["name", "area", "status", "data_abertura", "modified"],
		limit_page_length=0,
	)

	if period_start:
		servicos = [
			s
			for s in servicos
			if s.data_abertura and getdate(s.data_abertura) >= getdate(period_start)
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
			if s.data_abertura:
				bucket["dias_encerramento"].append(
					date_diff(getdate(s.modified), getdate(s.data_abertura))
				)

	honorarios = _sum_honorarios_by_servico()
	custas = _sum_custas_by_servico()
	horas = _sum_horas_by_servico() if cint(filters.get("incluir_horas", 1)) else {}

	rows = []
	chart_labels = []
	honorarios_chart = []
	custas_chart = []

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

	chart = None
	if chart_labels:
		chart = {
			"data": {
				"labels": chart_labels,
				"datasets": [
					{"name": _("Honorários"), "values": honorarios_chart},
					{"name": _("Custas"), "values": custas_chart},
				],
			},
			"type": "bar",
		}

	return rows, chart


def _sum_honorarios_by_servico():
	result = defaultdict(float)
	for row in frappe.get_all(
		"Acordo de Honorarios Processuais",
		fields=["servico", "valor_total_do_acordo"],
		limit_page_length=0,
	):
		if row.servico:
			result[row.servico] += flt(row.valor_total_do_acordo)
	return result


def _sum_custas_by_servico():
	if not frappe.db.table_exists("Custa Processual"):
		return defaultdict(float)
	result = defaultdict(float)
	for row in frappe.get_all(
		"Custa Processual",
		filters={"status": ["in", ["Pago", "Repassado"]]},
		fields=["servico", "valor"],
		limit_page_length=0,
	):
		if row.servico:
			result[row.servico] += flt(row.valor)
	return result


def _sum_horas_by_servico():
	if not frappe.db.table_exists("Registro de Horas"):
		return defaultdict(float)
	result = defaultdict(float)
	for row in frappe.get_all(
		"Registro de Horas",
		fields=["servico", "duracao_horas"],
		limit_page_length=0,
	):
		if row.servico:
			result[row.servico] += flt(row.duracao_horas)
	return result
