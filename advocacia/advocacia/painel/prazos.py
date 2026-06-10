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
		"Deadline",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, amanha]],
		},
		fields=["name", "description", "due_date", "client", "legal_case", "priority"],
		order_by="due_date asc",
		limit_page_length=20,
	)
	cliente_nome_map = _cliente_nome_lookup([p.client for p in prazos_criticos if p.client])
	for p in prazos_criticos:
		dias = date_diff(p.due_date, hoje)
		alertas.append(
			{
				"type": "prazo",
				"nivel": "red" if dias <= 0 else "yellow",
				"title": p.description or p.name,
				"date": p.due_date,
				"client": p.client or "",
				"cliente_nome": cliente_nome_map.get(p.client, p.client or ""),
				"dias": dias,
				"doctype": "Deadline",
				"docname": p.name,
			}
		)

	audiencias_hoje = frappe.get_all(
		"Hearing",
		filters={"hearing_datetime": ["between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]]},
		fields=["name", "client", "hearing_datetime", "type", "court_branch", "modality"],
		order_by="hearing_datetime asc",
		limit_page_length=20,
	)
	cliente_nome_aud = _cliente_nome_lookup([a.client for a in audiencias_hoje if a.client])
	for a in audiencias_hoje:
		alertas.append(
			{
				"type": "audiencia",
				"nivel": "yellow",
				"title": a.type or _("Audiência"),
				"date": str(a.hearing_datetime)[:10] if a.hearing_datetime else hoje,
				"hora": str(a.hearing_datetime)[11:16] if a.hearing_datetime else "",
				"client": a.client or "",
				"cliente_nome": cliente_nome_aud.get(a.client, a.client or ""),
				"court_branch_link": _vara_label(a.court_branch),
				"modality": a.modality or "",
				"doctype": "Hearing",
				"docname": a.name,
			}
		)

	return alertas
def _build_centro_atencao(hoje, amanha, kpis, financeiro, tarefas):
	previsto = financeiro.get("previsto_periodo") or financeiro.get("previsto_semana") or {"count": 0, "amount": 0}
	return {
		"audiencias_hoje": kpis.get("audiencias_hoje") or 0,
		"audiencias_amanha": kpis.get("audiencias_amanha") or 0,
		"audiencias_periodo": kpis.get("audiencias_semana") or 0,
		"prazos_vencidos": kpis.get("prazos_vencidos") or 0,
		"prazos_proximos_3d": kpis.get("prazos_criticos") or 0,
		"prazos_urgentes": kpis.get("prazos_urgentes") or 0,
		"legal_tasks_atrasadas": kpis.get("legal_tasks_atrasadas") or 0,
		"legal_tasks_pendentes": kpis.get("legal_tasks_pendentes") or 0,
		"fee_installments_vencidas": kpis.get("fee_installments_vencidas") or {"count": 0, "amount": 0},
		"payments_periodo": previsto,
		"recebimentos_periodo": kpis.get("recebido_periodo") or {"count": 0, "amount": 0},
		"honorarios_ativos": kpis.get("honorarios_ativos") or 0,
		"custas_abertas": kpis.get("custas_abertas") or 0,
		"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
		"legal_cases_ativos": kpis.get("legal_cases_ativos") or 0,
		"total_clientes": kpis.get("total_clientes") or 0,
	}
def _get_audiencias(hoje, periodo_fim, limit):
	rows = frappe.get_all(
		"Hearing",
		filters={"hearing_datetime": ["between", [f"{hoje} 00:00:00", f"{periodo_fim} 23:59:59"]]},
		fields=[
			"name",
			"legal_case",
			"client",
			"hearing_datetime",
			"type",
			"court_branch",
			"modality",
			"link_virtual",
		],
		order_by="hearing_datetime asc",
		limit_page_length=limit,
	)
	servico_map = _servico_lookup(
		[a.legal_case for a in rows if a.get("legal_case")],
		["client", "title"],
	)
	cliente_por_servico = {name: sv.client for name, sv in servico_map.items()}
	cliente_nome_map = _cliente_nome_lookup(
		[a.client for a in rows if a.client] + [sv.client for sv in servico_map.values() if sv.client]
	)
	for a in rows:
		data_hora = a.get("hearing_datetime")
		if data_hora:
			a["date"] = str(data_hora)[:10]
			a["hora"] = str(data_hora)[11:16]
			a["dias_restantes"] = date_diff(a["date"], hoje)
		else:
			a["date"] = None
			a["hora"] = ""
			a["dias_restantes"] = 0
		a["vara_label"] = _vara_label(a.get("court_branch"))
		if a.get("legal_case") and not a.get("client"):
			a["client"] = cliente_por_servico.get(a.legal_case) or ""
		a["cliente_nome"] = cliente_nome_map.get(a.get("client"), a.get("client") or "")
		sv = servico_map.get(a.get("legal_case")) if a.get("legal_case") else None
		a["servico_titulo"] = (sv.title if sv else "") or ""
	return rows
def _get_prazos(hoje, periodo_fim, limit):
	rows = frappe.get_all(
		"Deadline",
		filters={
			"status": "Pendente",
			"due_date": ["<=", periodo_fim],
		},
		fields=["name", "description", "due_date", "priority", "legal_case", "client"],
		order_by="due_date asc",
		limit_page_length=limit * 3,
	)
	prioridade_ordem = {"Alta": 0, "Média": 1, "Media": 1, "Baixa": 2, "Normal": 3}
	servico_map = _servico_lookup(
		[p.legal_case for p in rows if p.legal_case], ["client", "title", "case_number"]
	)
	cliente_nome_map = _cliente_nome_lookup(
		[p.client for p in rows if p.client]
		+ [sv.client for sv in servico_map.values() if sv.client]
	)
	for p in rows:
		p["dias_restantes"] = date_diff(p.due_date, hoje) if p.due_date else 0
		p["cliente_nome"] = cliente_nome_map.get(p.client, p.client or "")
		p["servico_titulo"] = ""
		p["case_number"] = ""
		if p.legal_case:
			sv = servico_map.get(p.legal_case)
			if sv:
				if not p["cliente_nome"]:
					p["cliente_nome"] = cliente_nome_map.get(sv.client, sv.client or "")
				p["servico_titulo"] = sv.title or ""
				p["case_number"] = sv.case_number or ""
	rows.sort(
		key=lambda x: (
			prioridade_ordem.get(x.get("priority"), 9),
			x.get("dias_restantes", 99),
		)
	)
	return rows[:limit]
