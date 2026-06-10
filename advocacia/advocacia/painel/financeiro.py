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
	"origin_type",
	"fee_agreement",
	"service_record",
	"client",
	"legal_case",
	"amount",
	"due_date",
	"status",
	"description",
	"installment_number",
]
def _build_financeiro(hoje, periodo_fim, mes_inicio, mes_fim, kpis, periodo_dias=7):
	previsto_periodo_rows = frappe.get_all(
		"Legal Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, periodo_fim]],
		},
		fields=["amount"],
		limit_page_length=500,
	)
	previsto_periodo_valor = sum(flt(p.amount) for p in previsto_periodo_rows)
	previsto_periodo = {
		"count": len(previsto_periodo_rows),
		"amount": previsto_periodo_valor,
	}
	vencido_valor = flt(kpis["fee_installments_vencidas"]["amount"])
	recebido_valor = flt(kpis["recebido_mes"]["amount"])
	pendente_valor = flt(kpis["fee_installments_a_vencer_30d"]["amount"])
	base_inadimplencia = vencido_valor + recebido_valor + pendente_valor
	taxa_inadimplencia = (
		round((vencido_valor / base_inadimplencia) * 100, 1) if base_inadimplencia else 0
	)

	periodo_label = _("hoje") if periodo_dias == 1 else _("{0} dias").format(periodo_dias)
	return {
		"recebido_mes": kpis["recebido_mes"],
		"recebido_hoje": kpis.get("recebido_hoje") or {"count": 0, "amount": 0},
		"recebido_periodo": kpis.get("recebido_periodo") or {"count": 0, "amount": 0},
		"vencido": kpis["fee_installments_vencidas"],
		"previsto_mes": kpis["previsto_mes"],
		"previsto_periodo": previsto_periodo,
		"previsto_semana": previsto_periodo,
		"a_vencer_30d": kpis["fee_installments_a_vencer_30d"],
		"taxa_inadimplencia": taxa_inadimplencia,
		"taxa_recebimento": kpis.get("taxa_recebimento") or 0,
		"grafico": [
			{"label": _("Vencido"), "amount": vencido_valor, "tone": "danger"},
			{"label": _("Recebido (mês)"), "amount": recebido_valor, "tone": "success"},
			{"label": _("A vencer ({0})").format(periodo_label), "amount": pendente_valor, "tone": "warning"},
			{"label": _("Previsto mês"), "amount": flt(kpis["previsto_mes"]["amount"]), "tone": "neutral"},
		],
	}
def _enriquecer_pagamentos(pagamentos, hoje):
	cache_servico = _servico_lookup(
		[p.get("legal_case") for p in pagamentos if p.get("legal_case")],
		["title", "type", "case_number", "client"],
	)
	cliente_links = set()
	for p in pagamentos:
		if p.get("client"):
			cliente_links.add(p.get("client"))
		servico = p.get("legal_case")
		if servico:
			sv_cliente = (cache_servico.get(servico) or {}).get("client")
			if sv_cliente:
				cliente_links.add(sv_cliente)
	cliente_nomes = _cliente_nome_lookup(cliente_links)

	for p in pagamentos:
		p["parent"] = p.get("fee_agreement") or p.get("service_record")
		p["total_amount"] = p.get("amount")
		p["due_date"] = p.get("due_date")
		p["origem_label"] = _pagamento_origem_label(p)

		cliente_link = p.get("client")
		p["cliente_nome"] = cliente_nomes.get(cliente_link, cliente_link or "")

		servico = p.get("legal_case")
		p["servico_ref"] = servico or ""
		p["servico_titulo"] = ""
		p["servico_tipo"] = ""
		p["case_number"] = ""
		if servico:
			sv = cache_servico.get(servico) or {}
			p["servico_titulo"] = sv.get("title") or ""
			p["servico_tipo"] = sv.get("type") or ""
			p["case_number"] = sv.get("case_number") or ""
			if not p.get("client") and sv.get("client"):
				p["cliente_nome"] = cliente_nomes.get(sv.get("client"), sv.get("client"))

		vencimento = p.get("due_date")
		if vencimento:
			p["dias_atraso"] = max(date_diff(hoje, vencimento), 0)
			p["dias_para_vencer"] = max(date_diff(vencimento, hoje), 0)
		else:
			p["dias_atraso"] = 0
			p["dias_para_vencer"] = 0

	return pagamentos
def _get_custas_pendentes_repasse(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Court Cost", "read"):
		return []
	if not frappe.db.table_exists("Court Cost"):
		return []
	rows = frappe.get_all(
		"Court Cost",
		filters={"bill_to_client": 1, "status": "Pago"},
		fields=["name", "description", "type", "amount", "legal_case", "client", "payment_date"],
		order_by="payment_date ASC",
		limit=min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX),
	)
	servico_map = _servico_lookup([c.legal_case for c in rows if c.legal_case], ["client", "title"])
	cliente_nome_map = _cliente_nome_lookup(
		[c.client for c in rows if c.client]
		+ [sv.client for sv in servico_map.values() if sv.client]
	)
	for c in rows:
		c["cliente_nome"] = cliente_nome_map.get(c.client, c.client or "")
		sv = servico_map.get(c.legal_case) if c.legal_case else None
		c["servico_titulo"] = (sv.title if sv else "") or ""
		if not c["cliente_nome"] and sv and sv.client:
			c["cliente_nome"] = cliente_nome_map.get(sv.client, sv.client)
	return rows
def _get_despesas_pendentes(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Office Expense", "read"):
		return []
	return frappe.get_all(
		"Office Expense",
		filters={"status": ["in", ["Pendente", "Atrasado"]]},
		fields=["name", "description", "category", "amount", "due_date", "status"],
		order_by="due_date ASC",
		limit=min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX),
	)
def _get_pagamentos_operacao(hoje, periodo_fim, limit_start, limit_page_length):
	"""Operação: vencidos + pendentes no período."""
	limit_page_length = min(cint(limit_page_length or LIST_LIMIT_MAX), LIST_LIMIT_MAX)
	vencidos = frappe.get_all(
		"Legal Payment",
		filters={"status": "Vencido"},
		fields=PAGAMENTO_FIELDS,
		order_by="due_date asc",
		limit_page_length=limit_page_length,
	)
	proximos = frappe.get_all(
		"Legal Payment",
		filters={
			"status": "Pendente",
			"due_date": ["between", [hoje, periodo_fim]],
		},
		fields=PAGAMENTO_FIELDS,
		order_by="due_date asc",
		limit_start=limit_start,
		limit_page_length=limit_page_length,
	)
	rows = vencidos + proximos
	return _enriquecer_pagamentos(rows[:limit_page_length], hoje)
def _get_total_custas_mes(mes_inicio, mes_fim):
	if not frappe.has_permission("Court Cost", "read"):
		return 0
	if not frappe.db.table_exists("Court Cost"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(amount), 0) as total
		FROM `tabCourt Cost`
		WHERE payment_date BETWEEN %s AND %s
		AND status IN ('Pago', 'Repassado')
		""",
		(mes_inicio, mes_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)
def _get_total_despesas_mes(mes_inicio, mes_fim):
	if not frappe.has_permission("Office Expense", "read"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(amount), 0) as total
		FROM `tabOffice Expense`
		WHERE due_date BETWEEN %s AND %s
		AND status != 'Cancelado'
		""",
		(mes_inicio, mes_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)
def _marcar_pagamento_recebido(pagamento_name):
	from advocacia.advocacia.financeiro import sync_parcela_from_pagamento

	doc = frappe.get_doc("Legal Payment", pagamento_name)
	if doc.status == "Cancelado":
		frappe.throw(_("Legal Payment cancelado não pode ser alterado."))
	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(_("Legal Payment já está {0}").format(doc.status))

	doc.status = "Recebido"
	doc.received_date = today()
	doc.received_amount = flt(doc.received_amount) or flt(doc.amount)
	doc.save(ignore_permissions=False)
	sync_parcela_from_pagamento(doc)

	return {"ok": True, "name": doc.name, "parent": doc.fee_agreement}
def _marcar_parcela_legado_recebida(parcela_name):
	"""Fallback para parcelas ainda sem Legal Payment vinculado."""
	doc = frappe.get_doc("Fee Installment", parcela_name)
	if doc.status in ("Recebido", "Repassado"):
		frappe.throw(_("Parcela já está {0}").format(doc.status))

	doc.status = "Recebido"
	doc.received_date = today()
	doc.save(ignore_permissions=False)
	if doc.parent:
		acordo = frappe.get_doc("Fee Agreement", doc.parent)
		from advocacia.advocacia.financeiro import sincronizar_pagamentos_do_acordo

		sincronizar_pagamentos_do_acordo(acordo)

	return {"ok": True, "name": doc.name, "parent": doc.parent}
def _pagamento_origem_label(pagamento):
	if pagamento.get("fee_agreement"):
		return (
			frappe.db.get_value("Fee Agreement", pagamento.fee_agreement, "title")
			or pagamento.fee_agreement
		)
	if pagamento.get("service_record"):
		registro_title = frappe.db.get_value("Service Record", pagamento.service_record, "title")
		return _("Atos: {0}").format(registro_title or pagamento.service_record)
	return pagamento.get("origin_type") or ""
def _vara_label(vara_link):
	if not vara_link:
		return ""
	try:
		return frappe.db.get_value("Court Branch", vara_link, "court_branch_name") or vara_link
	except frappe.DoesNotExistError:
		return vara_link
	except Exception:
		frappe.log_error(
			title="Advocacia painel _vara_label",
			message=frappe.get_traceback(),
		)
		return vara_link
def marcar_parcela(parcela_name: str) -> dict:
	"""Marca Legal Payment como Recebido (compat: parametro parcela_name = name do Legal Payment)."""
	frappe.has_permission("Legal Payment", "write", throw=True)

	if frappe.db.exists("Legal Payment", parcela_name):
		return _marcar_pagamento_recebido(parcela_name)

	if frappe.db.exists("Fee Installment", parcela_name):
		return _marcar_parcela_legado_recebida(parcela_name)

	frappe.throw(_("Registro financeiro não encontrado."))
