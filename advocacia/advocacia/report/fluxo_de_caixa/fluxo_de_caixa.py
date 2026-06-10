# Copyright (c) 2026, Advocacia and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import add_months, cint, flt, get_first_day, get_last_day, getdate, today

from advocacia.advocacia.report_visuals import CASH_IN_OUT, bar_chart, currency_summary, month_label


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "date", "label": _("Data"), "fieldtype": "Date", "width": 110},
		{"fieldname": "type", "label": _("Tipo"), "fieldtype": "Data", "width": 90},
		{"fieldname": "description", "label": _("Descrição"), "fieldtype": "Data", "width": 220},
		{"fieldname": "origem", "label": _("Origem"), "fieldtype": "Data", "width": 160},
		{"fieldname": "origem_doctype", "label": _("Origem DocType"), "fieldtype": "Data", "hidden": 1},
		{
			"fieldname": "documento",
			"label": _("Documento"),
			"fieldtype": "Dynamic Link",
			"options": "origem_doctype",
			"width": 140,
		},
		{
			"fieldname": "valor_entrada",
			"label": _("Valor Entrada"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "valor_saida",
			"label": _("Valor Saída"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "saldo_acumulado",
			"label": _("Saldo Acumulado"),
			"fieldtype": "Currency",
			"width": 140,
		},
	]


def _get_period_bounds(filters):
	hoje = getdate(today())
	meses = int(filters.get("meses") or 6)
	period_start = get_first_day(hoje)
	period_end = get_last_day(add_months(period_start, meses - 1))
	return period_start, period_end, meses


def _get_pagamentos(filters, period_start, period_end):
	query_filters = {
		"status": "Recebido",
		"received_date": ["between", [period_start, period_end]],
	}
	if filters.get("client"):
		query_filters["client"] = filters.client

	return frappe.get_all(
		"Legal Payment",
		filters=query_filters,
		fields=["name", "description", "received_date", "amount", "received_amount"],
		order_by="received_date asc",
		limit_page_length=0,
	)


def _get_despesas(filters, period_start, period_end):
	if not cint(filters.get("incluir_despesas", 1)):
		return []

	return frappe.get_all(
		"Office Expense",
		filters={
			"status": "Pago",
			"payment_date": ["between", [period_start, period_end]],
		},
		fields=["name", "description", "category", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=0,
	)


def _get_custas(filters, period_start, period_end):
	if not frappe.db.table_exists("Court Cost"):
		return []

	custa_filters = {
		"status": "Pago",
		"payment_date": ["between", [period_start, period_end]],
	}
	if filters.get("client"):
		custa_filters["client"] = filters.client

	return frappe.get_all(
		"Court Cost",
		filters=custa_filters,
		fields=["name", "description", "type", "legal_case", "payment_date", "amount"],
		order_by="payment_date asc",
		limit_page_length=0,
	)


def _build_chart(transactions, period_start, meses):
	month_totals = {}
	for i in range(meses):
		month_start = get_first_day(add_months(period_start, i))
		label = month_label(month_start)
		month_totals[label] = {"entrada": 0.0, "saida": 0.0}

	for row in transactions:
		label = month_label(row["date"])
		if label not in month_totals:
			month_totals[label] = {"entrada": 0.0, "saida": 0.0}
		month_totals[label]["entrada"] += flt(row.get("valor_entrada"))
		month_totals[label]["saida"] += flt(row.get("valor_saida"))

	labels = list(month_totals.keys())
	return bar_chart(
		labels,
		[
			{"name": _("Entradas"), "values": [month_totals[l]["entrada"] for l in labels]},
			{"name": _("Saídas"), "values": [month_totals[l]["saida"] for l in labels]},
		],
		CASH_IN_OUT,
	)


def _get_data(filters):
	period_start, period_end, meses = _get_period_bounds(filters)
	transactions = []

	for pag in _get_pagamentos(filters, period_start, period_end):
		valor = flt(pag.received_amount or pag.amount)
		transactions.append(
			{
				"date": pag.received_date,
				"type": _("Entrada"),
				"description": pag.description or pag.name,
				"origem": "Legal Payment",
				"origem_doctype": "Legal Payment",
				"documento": pag.name,
				"valor_entrada": valor,
				"valor_saida": 0,
			}
		)

	for desp in _get_despesas(filters, period_start, period_end):
		descricao = desp.description or desp.name
		if desp.category:
			descricao = f"{descricao} ({desp.category})"
		transactions.append(
			{
				"date": desp.payment_date,
				"type": _("Saída"),
				"description": descricao,
				"origem": "Office Expense",
				"origem_doctype": "Office Expense",
				"documento": desp.name,
				"valor_entrada": 0,
				"valor_saida": flt(desp.amount),
			}
		)

	for custa in _get_custas(filters, period_start, period_end):
		descricao = custa.description or custa.name
		if custa.type:
			descricao = f"{descricao} ({custa.type})"
		if custa.legal_case:
			descricao = f"{descricao} - {custa.legal_case}"
		transactions.append(
			{
				"date": custa.payment_date,
				"type": _("Saída"),
				"description": descricao,
				"origem": "Court Cost",
				"origem_doctype": "Court Cost",
				"documento": custa.name,
				"valor_entrada": 0,
				"valor_saida": flt(custa.amount),
			}
		)

	transactions.sort(key=lambda row: getdate(row["date"]))

	saldo = 0.0
	total_entradas = 0.0
	total_saidas = 0.0
	rows = []

	for row in transactions:
		total_entradas += flt(row["valor_entrada"])
		total_saidas += flt(row["valor_saida"])
		saldo += flt(row["valor_entrada"]) - flt(row["valor_saida"])
		row["saldo_acumulado"] = saldo
		rows.append(row)

	saldo_liquido = total_entradas - total_saidas

	if rows:
		rows.append({})
		rows.append(
			{
				"date": None,
				"type": "",
				"description": _("Total Entradas"),
				"origem": "",
				"origem_doctype": "",
				"documento": "",
				"valor_entrada": total_entradas,
				"valor_saida": 0,
				"saldo_acumulado": None,
			}
		)
		rows.append(
			{
				"date": None,
				"type": "",
				"description": _("Total Saídas"),
				"origem": "",
				"origem_doctype": "",
				"documento": "",
				"valor_entrada": 0,
				"valor_saida": total_saidas,
				"saldo_acumulado": None,
			}
		)
		rows.append(
			{
				"date": None,
				"type": "",
				"description": _("Saldo Líquido do Período"),
				"origem": "",
				"origem_doctype": "",
				"documento": "",
				"valor_entrada": 0,
				"valor_saida": 0,
				"saldo_acumulado": saldo_liquido,
			}
		)

	chart = _build_chart(transactions, period_start, meses) if transactions else None

	report_summary = [
		currency_summary(total_entradas, _("Total Entradas"), "Green"),
		currency_summary(total_saidas, _("Total Saídas"), "Red"),
		currency_summary(saldo_liquido, _("Saldo Líquido"), "Green" if saldo_liquido >= 0 else "Red"),
	]

	return rows, chart, report_summary
