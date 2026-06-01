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
	_effective_list_cap,
	_list_cap,
	_normalize_list_limit,
	_normalize_list_limits,
	_normalize_periodo_dias,
	_servico_lookup,
	_user_nome_lookup,
)

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
