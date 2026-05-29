import frappe
from frappe import _
from frappe.utils import (
	add_days,
	cint,
	date_diff,
	flt,
	get_first_day,
	get_last_day,
	today,
)

PAGAMENTO_FIELDS = [
	"name",
	"acordo",
	"cliente",
	"servico",
	"valor",
	"data_vencimento",
	"status",
	"descricao",
	"numero_parcela",
]


@frappe.whitelist()
def get_painel_data(limit_start=0, limit_page_length=20):
	if not frappe.has_permission("Servico", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	limit_start = cint(limit_start)
	limit_page_length = min(cint(limit_page_length or 20), 100)

	hoje = today()
	sete_dias = add_days(hoje, 7)
	mes_inicio = get_first_day(hoje)
	mes_fim = get_last_day(hoje)

	kpis = _build_kpis(hoje, sete_dias, mes_inicio, mes_fim)
	financeiro = _build_financeiro(hoje, sete_dias, mes_inicio, mes_fim, kpis)
	resumo = _build_resumo(hoje, kpis, financeiro)
	alertas = _build_alertas(hoje, sete_dias)
	parcelas = _get_pagamentos_operacao(hoje, sete_dias, limit_start, limit_page_length)
	audiencias = _get_audiencias(hoje, sete_dias)
	prazos = _get_prazos(hoje, sete_dias)
	tarefas = _get_tarefas(hoje, limit_start, limit_page_length)

	return {
		"kpis": kpis,
		"resumo": resumo,
		"financeiro": financeiro,
		"alertas": alertas,
		"parcelas": parcelas,
		"audiencias": audiencias,
		"prazos": prazos,
		"tarefas": tarefas,
	}


def _build_kpis(hoje, sete_dias, mes_inicio, mes_fim):
	vencidos = frappe.get_all(
		"Pagamento",
		filters={"status": "Vencido"},
		fields=["valor"],
		limit_page_length=500,
	)
	proximos_7d = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [hoje, sete_dias]],
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

	def _sum_valor(rows):
		return sum(flt(r.valor_recebido or r.valor) for r in rows)

	return {
		"total_clientes": frappe.db.count("Cliente"),
		"servicos_ativos": frappe.db.count("Servico", {"status": "Em andamento"}),
		"parcelas_vencidas": {
			"count": len(vencidos),
			"valor": sum(flt(p.valor) for p in vencidos),
		},
		"parcelas_a_vencer_30d": {
			"count": len(proximos_7d),
			"valor": sum(flt(p.valor) for p in proximos_7d),
		},
		"recebido_mes": {
			"count": len(recebidos_mes),
			"valor": _sum_valor(recebidos_mes),
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
		"audiencias_semana": frappe.db.count(
			"Audiencia",
			{"data_hora": ["between", [f"{hoje} 00:00:00", f"{sete_dias} 23:59:59"]]},
		),
		"prazos_urgentes": frappe.db.count(
			"Controle de Prazos",
			{
				"status": "Pendente",
				"data_prazo": ["<=", add_days(hoje, 3)],
			},
		),
	}


def _build_financeiro(hoje, sete_dias, mes_inicio, mes_fim, kpis):
	previsto_semana_rows = frappe.get_all(
		"Pagamento",
		filters={
			"status": "Pendente",
			"data_vencimento": ["between", [hoje, sete_dias]],
		},
		fields=["valor"],
		limit_page_length=500,
	)
	previsto_semana_valor = sum(flt(p.valor) for p in previsto_semana_rows)
	vencido_valor = flt(kpis["parcelas_vencidas"]["valor"])
	recebido_valor = flt(kpis["recebido_mes"]["valor"])
	pendente_valor = flt(kpis["parcelas_a_vencer_30d"]["valor"])
	base_inadimplencia = vencido_valor + recebido_valor + pendente_valor
	taxa_inadimplencia = (
		round((vencido_valor / base_inadimplencia) * 100, 1) if base_inadimplencia else 0
	)

	return {
		"recebido_mes": kpis["recebido_mes"],
		"recebido_hoje": kpis.get("recebido_hoje") or {"count": 0, "valor": 0},
		"vencido": kpis["parcelas_vencidas"],
		"previsto_mes": kpis["previsto_mes"],
		"previsto_semana": {
			"count": len(previsto_semana_rows),
			"valor": previsto_semana_valor,
		},
		"a_vencer_30d": kpis["parcelas_a_vencer_30d"],
		"taxa_inadimplencia": taxa_inadimplencia,
		"grafico": [
			{"label": _("Vencido"), "valor": vencido_valor, "tone": "danger"},
			{"label": _("Recebido"), "valor": recebido_valor, "tone": "success"},
			{"label": _("Próx. 7 dias"), "valor": pendente_valor, "tone": "warning"},
			{"label": _("Previsto mês"), "valor": flt(kpis["previsto_mes"]["valor"]), "tone": "neutral"},
		],
	}


def _build_resumo(hoje, kpis, financeiro):
	return {
		"data_hoje": frappe.utils.formatdate(hoje, "EEEE, d 'de' MMMM"),
		"audiencias_hoje": kpis.get("audiencias_hoje") or 0,
		"parcelas_vencidas": kpis["parcelas_vencidas"]["count"],
		"prazos_urgentes": kpis["prazos_urgentes"],
		"previsto_semana_valor": financeiro["previsto_semana"]["valor"],
		"urgencia": "alta"
		if kpis["parcelas_vencidas"]["count"] or kpis["prazos_urgentes"]
		else "normal",
	}


def _build_alertas(hoje, sete_dias):
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


def _get_pagamentos_operacao(hoje, sete_dias, limit_start, limit_page_length):
	"""Operação do dia: vencidos + pendentes nos próximos 7 dias."""
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
			"data_vencimento": ["between", [hoje, sete_dias]],
		},
		fields=PAGAMENTO_FIELDS,
		order_by="data_vencimento asc",
		limit_start=limit_start,
		limit_page_length=limit_page_length,
	)
	rows = vencidos + proximos
	return _enriquecer_pagamentos(rows, hoje)


def _get_audiencias(hoje, sete_dias):
	rows = frappe.get_all(
		"Audiencia",
		filters={"data_hora": ["between", [f"{hoje} 00:00:00", f"{sete_dias} 23:59:59"]]},
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
		limit_page_length=20,
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
			a["cliente"] = frappe.db.get_value("Servico", a.servico, "cliente") or ""
	return rows


def _get_prazos(hoje, sete_dias):
	rows = frappe.get_all(
		"Controle de Prazos",
		filters={
			"status": "Pendente",
			"data_prazo": ["<=", sete_dias],
		},
		fields=["name", "descricao", "data_prazo", "prioridade", "servico", "cliente"],
		order_by="data_prazo asc",
		limit_page_length=20,
	)
	prioridade_ordem = {"Alta": 0, "Média": 1, "Media": 1, "Baixa": 2, "Normal": 3}
	for p in rows:
		p["dias_restantes"] = date_diff(p.data_prazo, hoje) if p.data_prazo else 0
		p["cliente_nome"] = p.cliente or ""
		if p.servico:
			sv = frappe.db.get_value(
				"Servico", p.servico, ["cliente", "title", "numero_processo"], as_dict=True
			)
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
	return rows


def _get_tarefas(hoje, limit_start, limit_page_length):
	rows = frappe.get_all(
		"Tarefa",
		filters={"status": ["in", ["Pendente", "Em Andamento"]]},
		fields=["name", "titulo", "status", "prioridade", "data_limite", "servico", "responsavel"],
		order_by="data_limite asc, prioridade desc",
		limit_start=limit_start,
		limit_page_length=limit_page_length,
	)
	for t in rows:
		if t.data_limite:
			t["dias_restantes"] = date_diff(t.data_limite, hoje)
		else:
			t["dias_restantes"] = None
		t["cliente_nome"] = ""
		t["servico_titulo"] = ""
		if t.servico:
			sv = frappe.db.get_value(
				"Servico", t.servico, ["cliente", "title"], as_dict=True
			)
			if sv:
				t["cliente_nome"] = sv.cliente or ""
				t["servico_titulo"] = sv.title or ""
		if t.responsavel:
			t["responsavel_nome"] = frappe.db.get_value("User", t.responsavel, "full_name") or t.responsavel
		else:
			t["responsavel_nome"] = ""
	return rows


def _enriquecer_pagamentos(pagamentos, hoje):
	cache_servico = {}
	for p in pagamentos:
		p["parent"] = p.get("acordo")
		p["valor_total"] = p.get("valor")
		p["vencimento"] = p.get("data_vencimento")

		cliente_link = p.get("cliente")
		p["cliente_nome"] = cliente_link or ""
		if cliente_link and frappe.db.exists("Cliente", cliente_link):
			nome = frappe.db.get_value("Cliente", cliente_link, "nome")
			if nome:
				p["cliente_nome"] = nome

		servico = p.get("servico")
		p["servico_ref"] = servico or ""
		p["servico_titulo"] = ""
		p["servico_tipo"] = ""
		p["numero_processo"] = ""
		if servico:
			if servico not in cache_servico:
				cache_servico[servico] = frappe.db.get_value(
					"Servico",
					servico,
					["title", "tipo", "numero_processo", "cliente"],
					as_dict=True,
				) or {}
			sv = cache_servico[servico]
			p["servico_titulo"] = sv.get("title") or ""
			p["servico_tipo"] = sv.get("tipo") or ""
			p["numero_processo"] = sv.get("numero_processo") or ""
			if not p["cliente_nome"] and sv.get("cliente"):
				p["cliente_nome"] = sv.get("cliente")

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
	except Exception:
		return vara_link


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
	frappe.db.commit()

	return {"ok": True, "name": doc.name, "parent": doc.acordo}


def _marcar_parcela_legado_recebida(parcela_name):
	"""Fallback para parcelas ainda sem Pagamento vinculado."""
	doc = frappe.get_doc("Parcela de Honorarios", parcela_name)
	if doc.status in ("Recebida", "Repassada"):
		frappe.throw(_("Parcela já está {0}").format(doc.status))

	doc.status = "Recebida"
	doc.data_recebimento = today()
	doc.save(ignore_permissions=False)
	if doc.parent:
		acordo = frappe.get_doc("Acordo de Honorarios Processuais", doc.parent)
		from advocacia.advocacia.financeiro import sincronizar_pagamentos_do_acordo

		sincronizar_pagamentos_do_acordo(acordo)
	frappe.db.commit()

	return {"ok": True, "name": doc.name, "parent": doc.parent}
