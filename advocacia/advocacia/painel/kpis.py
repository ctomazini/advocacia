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
		"Pagamento",
		filters={"status": "Vencido"},
		fields=["valor"],
		limit_page_length=500,
	)
	proximos_periodo = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [hoje, periodo_fim]],
		},
		fields=["valor"],
		limit_page_length=500,
	)
	recebidos_mes = frappe.get_all(
		"Pagamento",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"data_recebimento": ["between", [mes_inicio, mes_fim]],
		},
		fields=["valor", "valor_recebido"],
		limit_page_length=500,
	)
	recebidos_periodo = frappe.get_all(
		"Pagamento",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"data_recebimento": ["between", [hoje, periodo_fim]],
		},
		fields=["valor", "valor_recebido"],
		limit_page_length=500,
	)
	recebidos_hoje = frappe.get_all(
		"Pagamento",
		filters={
			"status": ["in", ["Recebido", "Repassado"]],
			"data_recebimento": hoje,
		},
		fields=["valor", "valor_recebido"],
		limit_page_length=500,
	)
	previsto_mes = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [mes_inicio, mes_fim]],
		},
		fields=["valor"],
		limit_page_length=500,
	)

	tarefas_pendentes = frappe.db.count(
		"Tarefa", {"status": ["in", ["Pendente", "Em Andamento"]]}
	)
	tarefas_atrasadas = frappe.db.count(
		"Tarefa",
		{
			"status": ["in", ["Pendente", "Em Andamento"]],
			"data_limite": ["<", hoje],
		},
	)
	prazos_vencidos = frappe.db.count(
		"Controle de Prazos",
		{"status": "Pendente", "data_prazo": ["<", hoje]},
	)
	honorarios_ativos = frappe.db.count(
		"Acordo de Honorarios Processuais", {"status": "Vigente"}
	)
	custas_abertas = _count_custas_abertas()

	def _sum_valor(rows):
		return sum(flt(r.valor_recebido or r.valor) for r in rows)

	vencido_valor = sum(flt(p.valor) for p in vencidos)
	recebido_mes_valor = _sum_valor(recebidos_mes)
	base_taxa = vencido_valor + recebido_mes_valor + sum(flt(p.valor) for p in proximos_periodo)
	taxa_recebimento = round((recebido_mes_valor / base_taxa) * 100, 1) if base_taxa else 100

	return {
		"total_clientes": frappe.db.count("Cliente"),
		"servicos_ativos": frappe.db.count("Servico", {"status": "Em andamento"}),
		"parcelas_vencidas": {
			"count": len(vencidos),
			"valor": vencido_valor,
		},
		"parcelas_a_vencer_30d": {
			"count": len(proximos_periodo),
			"valor": sum(flt(p.valor) for p in proximos_periodo),
		},
		"recebido_mes": {
			"count": len(recebidos_mes),
			"valor": recebido_mes_valor,
		},
		"recebido_periodo": {
			"count": len(recebidos_periodo),
			"valor": _sum_valor(recebidos_periodo),
		},
		"recebido_hoje": {
			"count": len(recebidos_hoje),
			"valor": _sum_valor(recebidos_hoje),
		},
		"previsto_mes": {
			"count": len(previsto_mes),
			"valor": sum(flt(p.valor) for p in previsto_mes),
		},
		"audiencias_hoje": frappe.db.count(
			"Audiencia",
			{"data_hora": ["between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]]},
		),
		"audiencias_amanha": frappe.db.count(
			"Audiencia",
			{
				"data_hora": [
					"between",
					[f"{amanha} 00:00:00", f"{amanha} 23:59:59"],
				],
			},
		),
		"audiencias_semana": frappe.db.count(
			"Audiencia",
			{"data_hora": ["between", [f"{hoje} 00:00:00", f"{periodo_fim} 23:59:59"]]},
		),
		"prazos_urgentes": frappe.db.count(
			"Controle de Prazos",
			{
				"status": "Pendente",
				"data_prazo": ["<=", add_days(hoje, 3)],
			},
		),
		"prazos_vencidos": prazos_vencidos,
		"prazos_criticos": frappe.db.count(
			"Controle de Prazos",
			{
				"status": "Pendente",
				"data_prazo": ["between", [hoje, add_days(hoje, 3)]],
			},
		),
		"tarefas_pendentes": tarefas_pendentes,
		"tarefas_atrasadas": tarefas_atrasadas,
		"honorarios_ativos": honorarios_ativos,
		"custas_abertas": custas_abertas,
		"taxa_recebimento": taxa_recebimento,
	}
def _build_resumo(hoje, kpis, financeiro, periodo_dias=7):
	return {
		"data_hoje": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"periodo_dias": periodo_dias,
		"audiencias_hoje": kpis.get("audiencias_hoje") or 0,
		"parcelas_vencidas": kpis["parcelas_vencidas"]["count"],
		"prazos_urgentes": kpis["prazos_urgentes"],
		"previsto_periodo_valor": financeiro["previsto_periodo"]["valor"],
		"previsto_semana_valor": financeiro["previsto_periodo"]["valor"],
		"urgencia": "alta"
		if kpis["parcelas_vencidas"]["count"]
		or kpis["prazos_urgentes"]
		or kpis.get("tarefas_atrasadas")
		else "normal",
	}
def _count_custas_abertas():
	if not frappe.db.table_exists("Custa Processual"):
		return 0
	return frappe.db.count(
		"Custa Processual",
		{"status": ["in", ["Pendente", "Pago"]], "repassar_cliente": 1},
	)
