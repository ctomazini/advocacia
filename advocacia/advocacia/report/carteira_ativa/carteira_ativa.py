# Copyright (c) 2026, Advocacia and contributors
# License: MIT

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, now_datetime, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
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
		{"fieldname": "titulo", "label": _("Título"), "fieldtype": "Data", "width": 200},
		{
			"fieldname": "client",
			"label": _("Cliente"),
			"fieldtype": "Link",
			"options": "Client",
			"width": 160,
		},
		{"fieldname": "area", "label": _("Área"), "fieldtype": "Data", "width": 100},
		{"fieldname": "fase", "label": _("Case Phase"), "fieldtype": "Data", "width": 130},
		{
			"fieldname": "proximo_prazo",
			"label": _("Próximo Prazo"),
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"fieldname": "prazo_dias",
			"label": _("Dias p/ Prazo"),
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"fieldname": "proxima_audiencia",
			"label": _("Próxima Audiência"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "audiencia_tipo",
			"label": _("Tipo Audiência"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "situacao_financeira",
			"label": _("Situação Financeira"),
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"fieldname": "valor_pendente",
			"label": _("Valor Pendente (R$)"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "valor_vencido",
			"label": _("Valor Vencido (R$)"),
			"fieldtype": "Currency",
			"width": 130,
		},
	]


def _get_data(filters):
	hoje = getdate(today())
	agora = now_datetime()

	servico_filters = {"status": "Em andamento"}
	if filters.get("client"):
		servico_filters["client"] = filters.client
	if filters.get("area"):
		servico_filters["area"] = filters.area
	if filters.get("tipo"):
		servico_filters["tipo"] = filters.tipo

	servicos = frappe.get_all(
		"Legal Case",
		filters=servico_filters,
		fields=["name", "title", "client", "area", "case_phase"],
		limit_page_length=0,
	)

	if not servicos:
		return [], _empty_chart(), _empty_summary()

	names = [s.name for s in servicos]

	prazos = frappe.get_all(
		"Deadline",
		filters={
			"legal_case": ["in", names],
			"status": "Pendente",
			"data_prazo": [">=", hoje],
		},
		fields=["legal_case", "data_prazo"],
		order_by="data_prazo asc",
	)
	prazo_map = {}
	for p in prazos:
		if p.legal_case not in prazo_map:
			prazo_map[p.legal_case] = p

	audiencias = frappe.get_all(
		"Hearing",
		filters={"legal_case": ["in", names], "data_hora": [">=", agora]},
		fields=["legal_case", "data_hora", "tipo"],
		order_by="data_hora asc",
	)
	audiencia_map = {}
	for a in audiencias:
		if a.legal_case not in audiencia_map:
			audiencia_map[a.legal_case] = a

	pagamentos = frappe.get_all(
		"Legal Payment",
		filters={"legal_case": ["in", names], "status": ["not in", ["Cancelado"]]},
		fields=["legal_case", "status", "valor"],
		limit_page_length=0,
	)
	pag_map = defaultdict(lambda: {"pendente": 0.0, "vencido": 0.0})
	for p in pagamentos:
		if p.status == "Pendente":
			pag_map[p.legal_case]["pendente"] += flt(p.valor)
		elif p.status == "Vencido":
			pag_map[p.legal_case]["vencido"] += flt(p.valor)

	rows = []
	total_valor_pendente = 0.0
	total_valor_vencido = 0.0
	count_com_prazo_7d = 0
	count_inadimplente = count_em_dia = count_quitado = 0

	for s in servicos:
		prazo = prazo_map.get(s.name)
		audiencia = audiencia_map.get(s.name)
		fin = pag_map[s.name]
		valor_pendente = fin["pendente"]
		valor_vencido = fin["vencido"]

		prazo_dias = None
		proximo_prazo = None
		if prazo and prazo.data_prazo:
			proximo_prazo = getdate(prazo.data_prazo)
			prazo_dias = date_diff(proximo_prazo, hoje)
			if prazo_dias <= 7:
				count_com_prazo_7d += 1

		proxima_audiencia = None
		audiencia_tipo = None
		if audiencia and audiencia.data_hora:
			proxima_audiencia = getdate(audiencia.data_hora)
			audiencia_tipo = audiencia.tipo

		if valor_vencido > 0:
			situacao = _("🔴 Inadimplente")
			count_inadimplente += 1
		elif valor_pendente > 0:
			situacao = _("🟡 Em dia")
			count_em_dia += 1
		else:
			situacao = _("🟢 Quitado")
			count_quitado += 1

		total_valor_pendente += valor_pendente
		total_valor_vencido += valor_vencido

		rows.append(
			{
				"legal_case": s.name,
				"titulo": s.title or s.name,
				"client": s.client,
				"area": s.area or "",
				"fase": s.case_phase or "",
				"proximo_prazo": proximo_prazo,
				"prazo_dias": prazo_dias if prazo_dias is not None else 9999,
				"proxima_audiencia": proxima_audiencia,
				"audiencia_tipo": audiencia_tipo or "",
				"situacao_financeira": situacao,
				"valor_pendente": valor_pendente,
				"valor_vencido": valor_vencido,
			}
		)

	rows.sort(key=lambda r: (r["prazo_dias"], -flt(r["valor_vencido"])))

	for r in rows:
		if r["prazo_dias"] == 9999:
			r["prazo_dias"] = None

	chart = {
		"data": {
			"labels": [_("Inadimplente"), _("Em dia"), _("Quitado")],
			"datasets": [{"values": [count_inadimplente, count_em_dia, count_quitado]}],
		},
		"type": "donut",
		"colors": ["#dc2626", "#eab308", "#22c55e"],
	}

	report_summary = [
		{
			"value": len(rows),
			"label": _("Serviços Ativos"),
			"datatype": "Int",
			"indicator": "Blue",
		},
		{
			"value": total_valor_pendente,
			"label": _("Pendente"),
			"datatype": "Currency",
			"indicator": "Orange",
		},
		{
			"value": total_valor_vencido,
			"label": _("Vencido"),
			"datatype": "Currency",
			"indicator": "Red",
		},
		{
			"value": count_com_prazo_7d,
			"label": _("Prazos em 7 dias"),
			"datatype": "Int",
			"indicator": "Orange",
		},
	]

	return rows, chart, report_summary


def _empty_chart():
	return {
		"data": {"labels": [], "datasets": [{"values": []}]},
		"type": "donut",
	}


def _empty_summary():
	return [
		{"value": 0, "label": _("Serviços Ativos"), "datatype": "Int", "indicator": "Blue"},
	]
