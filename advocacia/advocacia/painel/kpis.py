import frappe
from frappe import _
from frappe.utils import (
	add_days,
	cint,
	date_diff,
	flt,
	get_first_day,
	get_last_day,
	getdate,
	today,
)

def _build_kpis(hoje, periodo_fim, mes_inicio, mes_fim):
	amanha = add_days(hoje, 1)
	vencidos = frappe.get_all(
		"Legal Payment",
		filters={"status": "Vencido"},
		fields=["amount"],
		limit_page_length=500,
	)
	proximos_periodo = frappe.get_all(
		"Legal Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, periodo_fim]],
		},
		fields=["amount"],
		limit_page_length=500,
	)
	recebidos_mes = frappe.get_all(
		"Legal Payment",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"received_date": ["between", [mes_inicio, mes_fim]],
		},
		fields=["amount", "received_amount"],
		limit_page_length=500,
	)
	recebidos_periodo = frappe.get_all(
		"Legal Payment",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"received_date": ["between", [hoje, periodo_fim]],
		},
		fields=["amount", "received_amount"],
		limit_page_length=500,
	)
	recebidos_hoje = frappe.get_all(
		"Legal Payment",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"received_date": hoje,
		},
		fields=["amount", "received_amount"],
		limit_page_length=500,
	)
	previsto_mes = frappe.get_all(
		"Legal Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [mes_inicio, mes_fim]],
		},
		fields=["amount"],
		limit_page_length=500,
	)

	tarefas_pendentes = frappe.db.count(
		"Legal Task", {"status": ["in", ["Pendente", "Em Andamento"]]}
	)
	tarefas_atrasadas = frappe.db.count(
		"Legal Task",
		{
			"status": ["in", ["Pendente", "Em Andamento"]],
			"due_date": ["<", hoje],
		},
	)
	prazos_vencidos = frappe.db.count(
		"Deadline",
		{"status": "Pendente", "due_date": ["<", hoje]},
	)
	honorarios_ativos = frappe.db.count(
		"Fee Agreement", {"status": "Vigente"}
	)
	custas_abertas = _count_custas_abertas()

	def _sum_valor(rows):
		return sum(flt(r.received_amount or r.amount) for r in rows)

	vencido_valor = sum(flt(p.amount) for p in vencidos)
	recebido_mes_valor = _sum_valor(recebidos_mes)
	base_taxa = vencido_valor + recebido_mes_valor + sum(flt(p.amount) for p in proximos_periodo)
	taxa_recebimento = round((recebido_mes_valor / base_taxa) * 100, 1) if base_taxa else 100

	fee_installments_vencidas = {
		"count": len(vencidos),
		"amount": vencido_valor,
	}
	fee_installments_a_vencer_30d = {
		"count": len(proximos_periodo),
		"amount": sum(flt(p.amount) for p in proximos_periodo),
	}

	return {
		"total_clientes": frappe.db.count("Client"),
		"legal_cases_ativos": frappe.db.count("Legal Case", {"status": "Em andamento"}),
		"fee_installments_vencidas": fee_installments_vencidas,
		"fee_installments_a_vencer_30d": fee_installments_a_vencer_30d,
		"recebido_mes": {
			"count": len(recebidos_mes),
			"amount": recebido_mes_valor,
		},
		"recebido_periodo": {
			"count": len(recebidos_periodo),
			"amount": _sum_valor(recebidos_periodo),
		},
		"recebido_hoje": {
			"count": len(recebidos_hoje),
			"amount": _sum_valor(recebidos_hoje),
		},
		"previsto_mes": {
			"count": len(previsto_mes),
			"amount": sum(flt(p.amount) for p in previsto_mes),
		},
		"audiencias_hoje": frappe.db.count(
			"Hearing",
			{"hearing_datetime": ["between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]]},
		),
		"audiencias_amanha": frappe.db.count(
			"Hearing",
			{
				"hearing_datetime": [
					"between",
					[f"{amanha} 00:00:00", f"{amanha} 23:59:59"],
				],
			},
		),
		"audiencias_semana": frappe.db.count(
			"Hearing",
			{"hearing_datetime": ["between", [f"{hoje} 00:00:00", f"{periodo_fim} 23:59:59"]]},
		),
		"prazos_urgentes": frappe.db.count(
			"Deadline",
			{
				"status": "Pendente",
				"due_date": ["<=", add_days(hoje, 3)],
			},
		),
		"prazos_vencidos": prazos_vencidos,
		"prazos_criticos": frappe.db.count(
			"Deadline",
			{
				"status": "Pendente",
				"due_date": ["between", [hoje, add_days(hoje, 3)]],
			},
		),
		"legal_tasks_pendentes": tarefas_pendentes,
		"legal_tasks_atrasadas": tarefas_atrasadas,
		"honorarios_ativos": honorarios_ativos,
		"custas_abertas": custas_abertas,
		"taxa_recebimento": taxa_recebimento,
	}
def _build_resumo(hoje, kpis, financeiro, periodo_dias=7):
	return {
		"data_hoje": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"periodo_dias": periodo_dias,
		"audiencias_hoje": kpis.get("audiencias_hoje") or 0,
		"fee_installments_vencidas": kpis["fee_installments_vencidas"]["count"],
		"prazos_urgentes": kpis["prazos_urgentes"],
		"previsto_periodo_valor": financeiro["previsto_periodo"]["amount"],
		"previsto_semana_valor": financeiro["previsto_periodo"]["amount"],
		"urgencia": "alta"
		if kpis["fee_installments_vencidas"]["count"]
		or kpis["prazos_urgentes"]
		or kpis.get("legal_tasks_atrasadas")
		else "normal",
	}
def _count_custas_abertas():
	if not frappe.db.table_exists("Court Cost"):
		return 0
	return frappe.db.count(
		"Court Cost",
		{"status": ["in", ["Pendente", "Pago"]], "bill_to_client": 1},
	)
