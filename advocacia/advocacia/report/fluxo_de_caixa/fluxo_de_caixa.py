# Copyright (c) 2026, Advocacia and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, today


MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = _get_columns()
	data, chart, report_summary = _get_data(filters)
	return columns, data, None, chart, report_summary


def _get_columns():
	return [
		{"fieldname": "periodo", "label": _("Período"), "fieldtype": "Data", "width": 120},
		{"fieldname": "previsto", "label": _("Previsto (R$)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "recebido", "label": _("Recebido (R$)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "vencido", "label": _("Vencido (R$)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "acumulado", "label": _("Acumulado (R$)"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "parcelas", "label": _("Parcelas"), "fieldtype": "Int", "width": 80},
	]


def _format_period_label(dt):
	dt = getdate(dt)
	return f"{MESES_PT[dt.month - 1]}/{dt.year}"


def _get_data(filters):
	hoje = getdate(today())
	meses = int(filters.get("meses") or 6)
	mes_inicio = get_first_day(hoje)

	query_filters = {"status": ["!=", "Cancelado"]}
	if filters.get("cliente"):
		query_filters["cliente"] = filters.cliente

	pagamentos = frappe.get_all(
		"Pagamento",
		filters=query_filters,
		fields=[
			"valor",
			"valor_recebido",
			"data_vencimento",
			"data_recebimento",
			"status",
		],
		limit_page_length=0,
	)

	rows = []
	total_previsto = 0.0
	total_recebido = 0.0
	total_vencido_acum = 0.0
	acumulado = 0.0

	chart_labels = []
	chart_previsto = []
	chart_recebido = []

	if filters.get("incluir_vencidos"):
		vencido_valor = 0.0
		vencido_count = 0
		for p in pagamentos:
			if p.status != "Vencido":
				continue
			if not p.data_vencimento or getdate(p.data_vencimento) >= mes_inicio:
				continue
			vencido_valor += flt(p.valor)
			vencido_count += 1
		if vencido_valor or vencido_count:
			rows.append(
				{
					"periodo": _("Vencidos"),
					"previsto": 0,
					"recebido": 0,
					"vencido": vencido_valor,
					"acumulado": 0,
					"parcelas": vencido_count,
				}
			)
			total_vencido_acum = vencido_valor

	for i in range(meses):
		period_start = get_first_day(add_months(mes_inicio, i))
		period_end = get_last_day(period_start)
		label = _format_period_label(period_start)

		previsto = recebido = vencido = 0.0
		parcelas = 0

		for p in pagamentos:
			dv = getdate(p.data_vencimento) if p.data_vencimento else None
			dr = getdate(p.data_recebimento) if p.data_recebimento else None

			in_month_venc = dv and period_start <= dv <= period_end
			in_month_rec = dr and period_start <= dr <= period_end

			if in_month_venc or in_month_rec:
				parcelas += 1

			if p.status == "Pendente" and in_month_venc:
				previsto += flt(p.valor)
			if p.status in ("Recebido", "Repassado") and in_month_rec:
				recebido += flt(p.valor_recebido or p.valor)
			if p.status == "Vencido" and in_month_venc:
				vencido += flt(p.valor)

		acumulado += recebido
		total_previsto += previsto
		total_recebido += recebido

		rows.append(
			{
				"periodo": label,
				"previsto": previsto,
				"recebido": recebido,
				"vencido": vencido,
				"acumulado": acumulado,
				"parcelas": parcelas,
			}
		)
		chart_labels.append(label)
		chart_previsto.append(previsto)
		chart_recebido.append(recebido)

	pct_realizacao = (total_recebido / total_previsto * 100) if total_previsto else 0

	chart = {
		"data": {
			"labels": chart_labels,
			"datasets": [
				{"name": _("Previsto"), "values": chart_previsto},
				{"name": _("Recebido"), "values": chart_recebido},
			],
		},
		"type": "line",
		"colors": ["#3b82f6", "#22c55e"],
	}

	report_summary = [
		{
			"value": total_previsto,
			"label": _("Total Previsto"),
			"datatype": "Currency",
			"indicator": "Blue",
		},
		{
			"value": total_recebido,
			"label": _("Total Recebido"),
			"datatype": "Currency",
			"indicator": "Green",
		},
		{
			"value": total_vencido_acum,
			"label": _("Vencido Acumulado"),
			"datatype": "Currency",
			"indicator": "Red",
		},
		{
			"value": pct_realizacao,
			"label": _("% Realização"),
			"datatype": "Percent",
			"indicator": "Green" if pct_realizacao >= 70 else "Orange",
		},
	]

	return rows, chart, report_summary
