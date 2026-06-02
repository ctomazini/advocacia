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

from advocacia.advocacia.painel._helpers import (
	LIST_LIMIT_MAX,
	_cliente_nome_lookup,
	_servico_lookup,
)
from advocacia.advocacia.painel.financeiro import _vara_label

def _build_alertas(hoje, periodo_fim):
	alertas = []
	amanha = add_days(hoje, 1)

	prazos_criticos = frappe.get_all(
		"Controle de Prazos",
		filters={
			"status": "Pendente",
			"data_prazo": ["between", [hoje, amanha]],
		},
		fields=["name", "descricao", "data_prazo", "cliente", "servico", "prioridade"],
		order_by="data_prazo asc",
		limit_page_length=20,
	)
	cliente_nome_map = _cliente_nome_lookup([p.cliente for p in prazos_criticos if p.cliente])
	for p in prazos_criticos:
		dias = date_diff(p.data_prazo, hoje)
		alertas.append(
			{
				"tipo": "prazo",
				"nivel": "red" if dias <= 0 else "yellow",
				"titulo": p.descricao or p.name,
				"data": p.data_prazo,
				"cliente": p.cliente or "",
				"cliente_nome": cliente_nome_map.get(p.cliente, p.cliente or ""),
				"dias": dias,
				"doctype": "Controle de Prazos",
				"docname": p.name,
			}
		)

	audiencias_hoje = frappe.get_all(
		"Audiencia",
		filters={"data_hora": ["between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]]},
		fields=["name", "cliente", "data_hora", "tipo", "local_vara", "modalidade"],
		order_by="data_hora asc",
		limit_page_length=20,
	)
	cliente_nome_aud = _cliente_nome_lookup([a.cliente for a in audiencias_hoje if a.cliente])
	for a in audiencias_hoje:
		alertas.append(
			{
				"tipo": "audiencia",
				"nivel": "yellow",
				"titulo": a.tipo or _("Audiência"),
				"data": str(a.data_hora)[:10] if a.data_hora else hoje,
				"hora": str(a.data_hora)[11:16] if a.data_hora else "",
				"cliente": a.cliente or "",
				"cliente_nome": cliente_nome_aud.get(a.cliente, a.cliente or ""),
				"vara": _vara_label(a.local_vara),
				"modalidade": a.modalidade or "",
				"doctype": "Audiencia",
				"docname": a.name,
			}
		)

	return alertas
def _build_centro_atencao(hoje, amanha, kpis, financeiro, tarefas):
	previsto = financeiro.get("previsto_periodo") or financeiro.get("previsto_semana") or {"count": 0, "valor": 0}
	return {
		"audiencias_hoje": kpis.get("audiencias_hoje") or 0,
		"audiencias_amanha": kpis.get("audiencias_amanha") or 0,
		"audiencias_periodo": kpis.get("audiencias_semana") or 0,
		"prazos_vencidos": kpis.get("prazos_vencidos") or 0,
		"prazos_proximos_3d": kpis.get("prazos_criticos") or 0,
		"prazos_urgentes": kpis.get("prazos_urgentes") or 0,
		"tarefas_atrasadas": kpis.get("tarefas_atrasadas") or 0,
		"tarefas_pendentes": kpis.get("tarefas_pendentes") or 0,
		"parcelas_vencidas": kpis.get("parcelas_vencidas") or {"count": 0, "valor": 0},
		"pagamentos_periodo": previsto,
		"recebimentos_periodo": kpis.get("recebido_periodo") or {"count": 0, "valor": 0},
		"honorarios_ativos": kpis.get("honorarios_ativos") or 0,
		"custas_abertas": kpis.get("custas_abertas") or 0,
		"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
		"servicos_ativos": kpis.get("servicos_ativos") or 0,
		"total_clientes": kpis.get("total_clientes") or 0,
	}
def _get_audiencias(hoje, periodo_fim, limit):
	rows = frappe.get_all(
		"Audiencia",
		filters={"data_hora": ["between", [f"{hoje} 00:00:00", f"{periodo_fim} 23:59:59"]]},
		fields=[
			"name",
			"servico",
			"cliente",
			"data_hora",
			"tipo",
			"local_vara",
			"modalidade",
			"link_virtual",
		],
		order_by="data_hora asc",
		limit_page_length=limit,
	)
	servico_map = _servico_lookup(
		[a.servico for a in rows if a.get("servico")],
		["cliente", "title"],
	)
	cliente_por_servico = {name: sv.cliente for name, sv in servico_map.items()}
	cliente_nome_map = _cliente_nome_lookup(
		[a.cliente for a in rows if a.cliente] + [sv.cliente for sv in servico_map.values() if sv.cliente]
	)
	for a in rows:
		data_hora = a.get("data_hora")
		if data_hora:
			a["data"] = str(data_hora)[:10]
			a["hora"] = str(data_hora)[11:16]
			a["dias_restantes"] = date_diff(a["data"], hoje)
		else:
			a["data"] = None
			a["hora"] = ""
			a["dias_restantes"] = 0
		a["vara_label"] = _vara_label(a.get("local_vara"))
		if a.get("servico") and not a.get("cliente"):
			a["cliente"] = cliente_por_servico.get(a.servico) or ""
		a["cliente_nome"] = cliente_nome_map.get(a.get("cliente"), a.get("cliente") or "")
		sv = servico_map.get(a.get("servico")) if a.get("servico") else None
		a["servico_titulo"] = (sv.title if sv else "") or ""
	return rows
def _get_prazos(hoje, periodo_fim, limit):
	rows = frappe.get_all(
		"Controle de Prazos",
		filters={
			"status": "Pendente",
			"data_prazo": ["<=", periodo_fim],
		},
		fields=["name", "descricao", "data_prazo", "prioridade", "servico", "cliente"],
		order_by="data_prazo asc",
		limit_page_length=limit * 3,
	)
	prioridade_ordem = {"Alta": 0, "Média": 1, "Media": 1, "Baixa": 2, "Normal": 3}
	servico_map = _servico_lookup(
		[p.servico for p in rows if p.servico], ["cliente", "title", "numero_processo"]
	)
	cliente_nome_map = _cliente_nome_lookup(
		[p.cliente for p in rows if p.cliente]
		+ [sv.cliente for sv in servico_map.values() if sv.cliente]
	)
	for p in rows:
		p["dias_restantes"] = date_diff(p.data_prazo, hoje) if p.data_prazo else 0
		p["cliente_nome"] = cliente_nome_map.get(p.cliente, p.cliente or "")
		p["servico_titulo"] = ""
		p["numero_processo"] = ""
		if p.servico:
			sv = servico_map.get(p.servico)
			if sv:
				if not p["cliente_nome"]:
					p["cliente_nome"] = cliente_nome_map.get(sv.cliente, sv.cliente or "")
				p["servico_titulo"] = sv.title or ""
				p["numero_processo"] = sv.numero_processo or ""
	rows.sort(
		key=lambda x: (
			prioridade_ordem.get(x.get("prioridade"), 9),
			x.get("dias_restantes", 99),
		)
	)
	return rows[:limit]
