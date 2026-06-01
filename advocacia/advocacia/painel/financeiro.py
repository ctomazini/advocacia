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
	_servico_lookup,
	_cliente_nome_lookup,
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
def _pagamento_origem_label(pagamento):
	if pagamento.get("acordo"):
		return pagamento.acordo
	if pagamento.get("registro_atos"):
		return _("Atos: {0}").format(pagamento.registro_atos)
	return pagamento.get("tipo_origem") or ""
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
def marcar_parcela(parcela_name):
	"""Marca Pagamento como Recebido (compat: parametro parcela_name = name do Pagamento)."""
	if not frappe.has_permission("Pagamento", "write"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	if frappe.db.exists("Pagamento", parcela_name):
		return _marcar_pagamento_recebido(parcela_name)

	if frappe.db.exists("Parcela de Honorarios", parcela_name):
		return _marcar_parcela_legado_recebida(parcela_name)

	frappe.throw(_("Registro financeiro não encontrado."))
