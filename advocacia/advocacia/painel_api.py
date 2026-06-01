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

PAGAMENTO_FIELDS = [
	"name",
	"tipo_origem",
	"acordo",
	"registro_atos",
	"cliente",
	"servico",
	"valor",
	"data_vencimento",
	"status",
	"descricao",
	"numero_parcela",
]

LIST_LIMIT_MAX = 100

DEFAULT_LIST_LIMIT_KEYS = (
	"timeline",
	"comunicacoes",
	"parcelas",
	"despesas",
	"custas",
)


def _normalize_periodo_dias(periodo_dias):
	dias = cint(periodo_dias or 7)
	if dias not in (1, 7, 15, 30):
		dias = 7
	return dias


def _normalize_list_limit(list_limit):
	val = cint(list_limit if list_limit is not None else 5)
	if val == 0:
		return 0
	if val not in (5, 10, 15):
		return 5
	return val


def _effective_list_cap(list_limit):
	if not list_limit:
		return LIST_LIMIT_MAX
	return list_limit


def _normalize_list_limits(list_limits=None, list_limit=None):
	defaults = {key: 5 for key in DEFAULT_LIST_LIMIT_KEYS}
	parsed = {}

	if list_limits:
		if isinstance(list_limits, str):
			parsed = frappe.parse_json(list_limits) or {}
		elif isinstance(list_limits, dict):
			parsed = list_limits

	legacy_limit = None
	if list_limit is not None:
		legacy_limit = _normalize_list_limit(list_limit)

	normalized = {}
	for key in DEFAULT_LIST_LIMIT_KEYS:
		if key in parsed:
			normalized[key] = _normalize_list_limit(parsed[key])
		elif legacy_limit is not None:
			normalized[key] = legacy_limit
		else:
			normalized[key] = defaults[key]

	return normalized


def _list_cap(list_limits, key):
	return _effective_list_cap(list_limits.get(key, 5))


def _servico_lookup(servico_names, extra_fields):
	names = list({name for name in servico_names if name})
	if not names:
		return {}
	fields = ["name"] + [f for f in extra_fields if f != "name"]
	rows = frappe.get_all("Servico", filters={"name": ["in", names]}, fields=fields)
	return {row.name: row for row in rows}


def _cliente_nome_lookup(cliente_names):
	names = list({name for name in cliente_names if name})
	if not names:
		return {}
	rows = frappe.get_all("Cliente", filters={"name": ["in", names]}, fields=["name", "nome"])
	return {row.name: row.nome or row.name for row in rows}


def _user_nome_lookup(user_names):
	names = list({name for name in user_names if name})
	if not names:
		return {}
	rows = frappe.get_all("User", filters={"name": ["in", names]}, fields=["name", "full_name"])
	return {row.name: row.full_name or row.name for row in rows}


@frappe.whitelist()
def get_painel_data(
	limit_start=0,
	limit_page_length=20,
	periodo_dias=7,
	list_limit=5,
	list_limits=None,
):
	if not frappe.has_permission("Servico", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	limit_start = cint(limit_start)
	limit_page_length = min(cint(limit_page_length or 20), 100)
	periodo_dias = _normalize_periodo_dias(periodo_dias)
	list_limits = _normalize_list_limits(list_limits, list_limit)
	list_limit = list_limits["timeline"]

	hoje = today()
	periodo_fim = add_days(hoje, periodo_dias)
	amanha = add_days(hoje, 1)
	mes_inicio = get_first_day(hoje)
	mes_fim = get_last_day(hoje)

	kpis = _build_kpis(hoje, periodo_fim, mes_inicio, mes_fim)
	financeiro = _build_financeiro(hoje, periodo_fim, mes_inicio, mes_fim, kpis, periodo_dias)
	resumo = _build_resumo(hoje, kpis, financeiro, periodo_dias)
	alertas = _build_alertas(hoje, periodo_fim)
	parcelas_cap = _list_cap(list_limits, "parcelas")
	despesas_cap = _list_cap(list_limits, "despesas")
	custas_cap = _list_cap(list_limits, "custas")
	comunicacoes_cap = _list_cap(list_limits, "comunicacoes")
	timeline_cap = _list_cap(list_limits, "timeline")
	tarefas_cap = timeline_cap

	parcelas_all = _get_pagamentos_operacao(
		hoje, periodo_fim, limit_start, LIST_LIMIT_MAX
	)
	parcelas = parcelas_all[:parcelas_cap]
	audiencias = _get_audiencias(hoje, periodo_fim, LIST_LIMIT_MAX)
	prazos = _get_prazos(hoje, periodo_fim, LIST_LIMIT_MAX)
	tarefas_all = _get_tarefas(hoje, limit_start, LIST_LIMIT_MAX)
	tarefas = tarefas_all[:tarefas_cap]
	despesas_all = _get_despesas_pendentes(LIST_LIMIT_MAX)
	despesas_pendentes = despesas_all[:despesas_cap]
	total_despesas_mes = _get_total_despesas_mes(mes_inicio, mes_fim)
	custas_all = _get_custas_pendentes_repasse(LIST_LIMIT_MAX)
	custas_pendentes_repasse = custas_all[:custas_cap]
	total_custas_mes = _get_total_custas_mes(mes_inicio, mes_fim)
	comunicacoes_all = _get_comunicacoes_pendentes(LIST_LIMIT_MAX)
	comunicacoes_pendentes = comunicacoes_all[:comunicacoes_cap]
	ultimas_comunicacoes = comunicacoes_pendentes or _get_ultimas_comunicacoes(
		comunicacoes_cap
	)
	horas_semana = _get_horas_semana(hoje)
	horas_periodo = _get_horas_periodo(hoje, periodo_fim)
	centro_atencao = _build_centro_atencao(hoje, amanha, kpis, financeiro, tarefas)
	timeline_full = _build_timeline(hoje, periodo_fim, audiencias, prazos, tarefas_all)
	timeline = timeline_full[:timeline_cap]

	list_meta = {
		"timeline": {"showing": len(timeline), "total": len(timeline_full)},
		"comunicacoes": {"showing": len(comunicacoes_pendentes), "total": len(comunicacoes_all)},
		"parcelas": {"showing": len(parcelas), "total": len(parcelas_all)},
		"despesas": {"showing": len(despesas_pendentes), "total": len(despesas_all)},
		"custas": {"showing": len(custas_pendentes_repasse), "total": len(custas_all)},
	}

	return {
		"periodo_dias": periodo_dias,
		"list_limit": list_limit,
		"list_limits": list_limits,
		"list_meta": list_meta,
		"kpis": kpis,
		"resumo": resumo,
		"financeiro": financeiro,
		"alertas": alertas,
		"centro_atencao": centro_atencao,
		"timeline": timeline,
		"parcelas": parcelas,
		"despesas_pendentes": despesas_pendentes,
		"total_despesas_mes": total_despesas_mes,
		"custas_pendentes_repasse": custas_pendentes_repasse,
		"total_custas_mes": total_custas_mes,
		"comunicacoes_pendentes": comunicacoes_pendentes,
		"ultimas_comunicacoes": ultimas_comunicacoes,
		"horas_semana": horas_semana,
		"horas_periodo": horas_periodo,
		"audiencias": audiencias[:timeline_cap],
		"prazos": prazos[:timeline_cap],
		"tarefas": tarefas,
	}


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


def _count_custas_abertas():
	if not frappe.db.table_exists("Custa Processual"):
		return 0
	return frappe.db.count(
		"Custa Processual",
		{"status": ["in", ["Pendente", "Pago"]], "repassar_cliente": 1},
	)


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


def _build_timeline(hoje, periodo_fim, audiencias, prazos, tarefas):
	items = []

	for a in audiencias or []:
		data_hora = a.get("data_hora")
		sort_key = str(data_hora) if data_hora else f"{a.get('data') or hoje} 23:59:00"
		items.append(
			{
				"tipo": "audiencia",
				"sort_key": sort_key,
				"data": a.get("data") or hoje,
				"hora": a.get("hora") or "",
				"titulo": a.get("tipo") or _("Audiência"),
				"subtitulo": a.get("cliente") or "",
				"detalhe": a.get("vara_label") or "",
				"doctype": "Audiencia",
				"docname": a.get("name"),
				"urgencia": "red" if a.get("dias_restantes") == 0 else "orange" if a.get("dias_restantes") == 1 else "blue",
			}
		)

	for p in prazos or []:
		dias = p.get("dias_restantes", 99)
		urgencia = "red" if dias < 0 else "orange" if dias <= 3 else "yellow"
		items.append(
			{
				"tipo": "prazo",
				"sort_key": f"{p.get('data_prazo') or hoje} 12:00:00",
				"data": p.get("data_prazo"),
				"hora": "",
				"titulo": p.get("descricao") or p.get("name"),
				"subtitulo": p.get("cliente_nome") or "",
				"detalhe": p.get("prioridade") or "",
				"doctype": "Controle de Prazos",
				"docname": p.get("name"),
				"urgencia": urgencia,
				"dias_restantes": dias,
			}
		)

	for t in tarefas or []:
		dias = t.get("dias_restantes")
		if t.get("data_limite"):
			sort_key = f"{t.get('data_limite')} 09:00:00"
			urgencia = "red" if dias is not None and dias < 0 else "orange" if dias == 0 else "yellow"
		else:
			sort_key = f"{hoje} 23:58:00"
			urgencia = "gray"
		items.append(
			{
				"tipo": "tarefa",
				"sort_key": sort_key,
				"data": t.get("data_limite") or hoje,
				"hora": "",
				"titulo": t.get("titulo") or t.get("name"),
				"subtitulo": t.get("cliente_nome") or t.get("responsavel_nome") or "",
				"detalhe": t.get("status") or "",
				"doctype": "Tarefa",
				"docname": t.get("name"),
				"urgencia": urgencia,
				"dias_restantes": dias,
			}
		)

	items.sort(key=lambda x: x.get("sort_key") or "")
	return items


def _build_financeiro(hoje, periodo_fim, mes_inicio, mes_fim, kpis, periodo_dias=7):
	previsto_periodo_rows = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [hoje, periodo_fim]],
		},
		fields=["valor"],
		limit_page_length=500,
	)
	previsto_periodo_valor = sum(flt(p.valor) for p in previsto_periodo_rows)
	previsto_periodo = {
		"count": len(previsto_periodo_rows),
		"valor": previsto_periodo_valor,
	}
	vencido_valor = flt(kpis["parcelas_vencidas"]["valor"])
	recebido_valor = flt(kpis["recebido_mes"]["valor"])
	pendente_valor = flt(kpis["parcelas_a_vencer_30d"]["valor"])
	base_inadimplencia = vencido_valor + recebido_valor + pendente_valor
	taxa_inadimplencia = (
		round((vencido_valor / base_inadimplencia) * 100, 1) if base_inadimplencia else 0
	)

	periodo_label = _("hoje") if periodo_dias == 1 else _("{0} dias").format(periodo_dias)
	return {
		"recebido_mes": kpis["recebido_mes"],
		"recebido_hoje": kpis.get("recebido_hoje") or {"count": 0, "valor": 0},
		"recebido_periodo": kpis.get("recebido_periodo") or {"count": 0, "valor": 0},
		"vencido": kpis["parcelas_vencidas"],
		"previsto_mes": kpis["previsto_mes"],
		"previsto_periodo": previsto_periodo,
		"previsto_semana": previsto_periodo,
		"a_vencer_30d": kpis["parcelas_a_vencer_30d"],
		"taxa_inadimplencia": taxa_inadimplencia,
		"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
		"grafico": [
			{"label": _("Vencido"), "valor": vencido_valor, "tone": "danger"},
			{"label": _("Recebido (mês)"), "valor": recebido_valor, "tone": "success"},
			{"label": _("A vencer ({0})").format(periodo_label), "valor": pendente_valor, "tone": "warning"},
			{"label": _("Previsto mês"), "valor": flt(kpis["previsto_mes"]["valor"]), "tone": "neutral"},
		],
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
	for p in prazos_criticos:
		dias = date_diff(p.data_prazo, hoje)
		alertas.append(
			{
				"tipo": "prazo",
				"nivel": "red" if dias <= 0 else "yellow",
				"titulo": p.descricao or p.name,
				"data": p.data_prazo,
				"cliente": p.cliente or "",
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
	for a in audiencias_hoje:
		alertas.append(
			{
				"tipo": "audiencia",
				"nivel": "yellow",
				"titulo": a.tipo or _("Audiência"),
				"data": str(a.data_hora)[:10] if a.data_hora else hoje,
				"hora": str(a.data_hora)[11:16] if a.data_hora else "",
				"cliente": a.cliente or "",
				"vara": _vara_label(a.local_vara),
				"modalidade": a.modalidade or "",
				"doctype": "Audiencia",
				"docname": a.name,
			}
		)

	return alertas


def _get_pagamentos_operacao(hoje, periodo_fim, limit_start, limit_page_length):
	"""Operação: vencidos + pendentes no período."""
	limit_page_length = min(cint(limit_page_length or LIST_LIMIT_MAX), LIST_LIMIT_MAX)
	vencidos = frappe.get_all(
		"Pagamento",
		filters={"status": "Vencido"},
		fields=PAGAMENTO_FIELDS,
		order_by="data_vencimento asc",
		limit_page_length=limit_page_length,
	)
	proximos = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [hoje, periodo_fim]],
		},
		fields=PAGAMENTO_FIELDS,
		order_by="data_vencimento asc",
		limit_start=limit_start,
		limit_page_length=limit_page_length,
	)
	rows = vencidos + proximos
	return _enriquecer_pagamentos(rows[:limit_page_length], hoje)


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
	servicos_sem_cliente = [
		a.servico for a in rows if a.get("servico") and not a.get("cliente")
	]
	cliente_por_servico = {
		sv.name: sv.cliente
		for sv in _servico_lookup(servicos_sem_cliente, ["cliente"]).values()
	}
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
	for p in rows:
		p["dias_restantes"] = date_diff(p.data_prazo, hoje) if p.data_prazo else 0
		p["cliente_nome"] = p.cliente or ""
		p["servico_titulo"] = ""
		p["numero_processo"] = ""
		if p.servico:
			sv = servico_map.get(p.servico)
			if sv:
				if not p["cliente_nome"]:
					p["cliente_nome"] = sv.cliente or ""
				p["servico_titulo"] = sv.title or ""
				p["numero_processo"] = sv.numero_processo or ""
	rows.sort(
		key=lambda x: (
			prioridade_ordem.get(x.get("prioridade"), 9),
			x.get("dias_restantes", 99),
		)
	)
	return rows[:limit]


def _get_tarefas(hoje, limit_start, limit):
	rows = frappe.get_all(
		"Tarefa",
		filters={"status": ["in", ["Pendente", "Em Andamento"]]},
		fields=["name", "titulo", "status", "prioridade", "data_limite", "servico", "responsavel"],
		order_by="data_limite asc, prioridade desc",
		limit_start=limit_start,
		limit_page_length=limit,
	)
	servico_map = _servico_lookup(
		[t.servico for t in rows if t.servico], ["cliente", "title"]
	)
	user_map = _user_nome_lookup([t.responsavel for t in rows if t.responsavel])
	for t in rows:
		if t.data_limite:
			t["dias_restantes"] = date_diff(t.data_limite, hoje)
		else:
			t["dias_restantes"] = None
		t["cliente_nome"] = ""
		t["servico_titulo"] = ""
		if t.servico:
			sv = servico_map.get(t.servico)
			if sv:
				t["cliente_nome"] = sv.cliente or ""
				t["servico_titulo"] = sv.title or ""
		t["responsavel_nome"] = user_map.get(t.responsavel) if t.responsavel else ""
	return rows


def _get_despesas_pendentes(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Despesa do Escritorio", "read"):
		return []
	return frappe.get_all(
		"Despesa do Escritorio",
		filters={"status": ["in", ["Pendente", "Atrasado"]]},
		fields=["name", "descricao", "categoria", "valor", "data_vencimento", "status"],
		order_by="data_vencimento ASC",
		limit=min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX),
	)


def _get_total_despesas_mes(mes_inicio, mes_fim):
	if not frappe.has_permission("Despesa do Escritorio", "read"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(valor), 0) as total
		FROM `tabDespesa do Escritorio`
		WHERE data_vencimento BETWEEN %s AND %s
		AND status != 'Cancelado'
		""",
		(mes_inicio, mes_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)


def _get_custas_pendentes_repasse(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Custa Processual", "read"):
		return []
	if not frappe.db.table_exists("Custa Processual"):
		return []
	return frappe.get_all(
		"Custa Processual",
		filters={"repassar_cliente": 1, "status": "Pago"},
		fields=["name", "descricao", "tipo", "valor", "servico", "cliente", "data_pagamento"],
		order_by="data_pagamento ASC",
		limit=min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX),
	)


def _get_total_custas_mes(mes_inicio, mes_fim):
	if not frappe.has_permission("Custa Processual", "read"):
		return 0
	if not frappe.db.table_exists("Custa Processual"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(valor), 0) as total
		FROM `tabCusta Processual`
		WHERE data_pagamento BETWEEN %s AND %s
		AND status IN ('Pago', 'Repassado')
		""",
		(mes_inicio, mes_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)


def _get_comunicacoes_pendentes(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Comunicacao", "read"):
		return []
	if not frappe.db.table_exists("Comunicacao"):
		return []

	hoje = today()
	rows = frappe.get_all(
		"Comunicacao",
		fields=[
			"name",
			"assunto",
			"tipo",
			"cliente",
			"servico",
			"data",
			"proximos_passos",
			"gerar_tarefa",
			"tarefa",
		],
		order_by="data asc",
		limit_page_length=LIST_LIMIT_MAX,
	)

	tarefa_status_map = {
		row.name: row.status
		for row in frappe.get_all(
			"Tarefa",
			filters={"name": ["in", list({c.tarefa for c in rows if c.tarefa})]},
			fields=["name", "status"],
		)
	}

	pendentes = []
	for c in rows:
		dias = date_diff(hoje, getdate(c.data)) if c.data else 0
		motivo = ""
		urgencia = 2

		if c.proximos_passos and not c.tarefa:
			motivo = _("Aguardando follow-up")
			urgencia = 0
		elif c.tarefa:
			status_tarefa = tarefa_status_map.get(c.tarefa)
			if status_tarefa in ("Pendente", "Em Andamento"):
				motivo = _("Tarefa em aberto")
				urgencia = 1
			else:
				continue
		elif c.gerar_tarefa:
			motivo = _("Retorno pendente")
			urgencia = 1
		elif dias >= 7:
			motivo = _("Sem contato recente")
			urgencia = 2
		else:
			continue

		c["dias_sem_retorno"] = dias
		c["motivo_pendencia"] = motivo
		c["urgencia_ordem"] = urgencia
		pendentes.append(c)

	pendentes.sort(key=lambda x: (x.get("urgencia_ordem", 9), -x.get("dias_sem_retorno", 0)))
	return pendentes[: min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX)]


def _get_ultimas_comunicacoes(limit=5):
	if not frappe.has_permission("Comunicacao", "read"):
		return []
	if not frappe.db.table_exists("Comunicacao"):
		return []
	return frappe.get_all(
		"Comunicacao",
		fields=["name", "assunto", "tipo", "cliente", "servico", "data"],
		order_by="data DESC",
		limit=min(cint(limit or 5), LIST_LIMIT_MAX),
	)


def _get_horas_semana(hoje):
	if not frappe.has_permission("Registro de Horas", "read"):
		return 0
	if not frappe.db.table_exists("Registro de Horas"):
		return 0
	week_start = add_days(hoje, -getdate(hoje).weekday())
	week_end = add_days(week_start, 6)
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(duracao_horas), 0) as total
		FROM `tabRegistro de Horas`
		WHERE data BETWEEN %s AND %s
		""",
		(week_start, week_end),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)


def _get_horas_periodo(hoje, periodo_fim):
	if not frappe.has_permission("Registro de Horas", "read"):
		return 0
	if not frappe.db.table_exists("Registro de Horas"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(duracao_horas), 0) as total
		FROM `tabRegistro de Horas`
		WHERE data BETWEEN %s AND %s
		""",
		(hoje, periodo_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)


def _enriquecer_pagamentos(pagamentos, hoje):
	cache_servico = _servico_lookup(
		[p.get("servico") for p in pagamentos if p.get("servico")],
		["title", "tipo", "numero_processo", "cliente"],
	)
	cliente_links = set()
	for p in pagamentos:
		if p.get("cliente"):
			cliente_links.add(p.get("cliente"))
		servico = p.get("servico")
		if servico:
			sv_cliente = (cache_servico.get(servico) or {}).get("cliente")
			if sv_cliente:
				cliente_links.add(sv_cliente)
	cliente_nomes = _cliente_nome_lookup(cliente_links)

	for p in pagamentos:
		p["parent"] = p.get("acordo") or p.get("registro_atos")
		p["valor_total"] = p.get("valor")
		p["vencimento"] = p.get("data_vencimento")
		p["origem_label"] = _pagamento_origem_label(p)

		cliente_link = p.get("cliente")
		p["cliente_nome"] = cliente_nomes.get(cliente_link, cliente_link or "")

		servico = p.get("servico")
		p["servico_ref"] = servico or ""
		p["servico_titulo"] = ""
		p["servico_tipo"] = ""
		p["numero_processo"] = ""
		if servico:
			sv = cache_servico.get(servico) or {}
			p["servico_titulo"] = sv.get("title") or ""
			p["servico_tipo"] = sv.get("tipo") or ""
			p["numero_processo"] = sv.get("numero_processo") or ""
			if not p.get("cliente") and sv.get("cliente"):
				p["cliente_nome"] = cliente_nomes.get(sv.get("cliente"), sv.get("cliente"))

		vencimento = p.get("data_vencimento")
		if vencimento:
			p["dias_atraso"] = max(date_diff(hoje, vencimento), 0)
			p["dias_para_vencer"] = max(date_diff(vencimento, hoje), 0)
		else:
			p["dias_atraso"] = 0
			p["dias_para_vencer"] = 0

	return pagamentos


def _vara_label(vara_link):
	if not vara_link:
		return ""
	try:
		return frappe.db.get_value("Vara", vara_link, "vara_name") or vara_link
	except frappe.DoesNotExistError:
		return vara_link
	except Exception:
		frappe.log_error(
			title="Advocacia painel _vara_label",
			message=frappe.get_traceback(),
		)
		return vara_link


def _pagamento_origem_label(pagamento):
	if pagamento.get("acordo"):
		return pagamento.acordo
	if pagamento.get("registro_atos"):
		return _("Atos: {0}").format(pagamento.registro_atos)
	return pagamento.get("tipo_origem") or ""


@frappe.whitelist()
def marcar_parcela_recebida(parcela_name):
	"""Marca Pagamento como Recebido (compat: parametro parcela_name = name do Pagamento)."""
	if not frappe.has_permission("Pagamento", "write"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	if frappe.db.exists("Pagamento", parcela_name):
		return _marcar_pagamento_recebido(parcela_name)

	if frappe.db.exists("Parcela de Honorarios", parcela_name):
		return _marcar_parcela_legado_recebida(parcela_name)

	frappe.throw(_("Registro financeiro não encontrado."))


def _marcar_pagamento_recebido(pagamento_name):
	from advocacia.advocacia.financeiro import sync_parcela_from_pagamento

	doc = frappe.get_doc("Pagamento", pagamento_name)
	if doc.status == "Cancelado":
		frappe.throw(_("Pagamento cancelado não pode ser alterado."))
	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(_("Pagamento já está {0}").format(doc.status))

	doc.status = "Recebido"
	doc.data_recebimento = today()
	doc.valor_recebido = flt(doc.valor_recebido) or flt(doc.valor)
	doc.save(ignore_permissions=False)
	sync_parcela_from_pagamento(doc)

	return {"ok": True, "name": doc.name, "parent": doc.acordo}


def _marcar_parcela_legado_recebida(parcela_name):
	"""Fallback para parcelas ainda sem Pagamento vinculado."""
	doc = frappe.get_doc("Parcela de Honorarios", parcela_name)
	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(_("Parcela já está {0}").format(doc.status))

	doc.status = "Recebido"
	doc.data_recebimento = today()
	doc.save(ignore_permissions=False)
	if doc.parent:
		acordo = frappe.get_doc("Acordo de Honorarios Processuais", doc.parent)
		from advocacia.advocacia.financeiro import sincronizar_pagamentos_do_acordo

		sincronizar_pagamentos_do_acordo(acordo)

	return {"ok": True, "name": doc.name, "parent": doc.parent}
