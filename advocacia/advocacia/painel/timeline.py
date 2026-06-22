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
		data_hora = a.get("hearing_datetime")
		sort_key = str(data_hora) if data_hora else f"{a.get('date') or hoje} 23:59:00"
		items.append(
			{
				"type": "audiencia",
				"sort_key": sort_key,
				"date": a.get("date") or hoje,
				"hora": a.get("hora") or "",
				"title": a.get("type") or _("Audiência"),
				"subtitle": a.get("cliente_nome") or a.get("client") or "",
				"detalhe": a.get("vara_label") or "",
				"doctype": "Hearing",
				"docname": a.get("name"),
				"urgencia": "red" if a.get("dias_restantes") == 0 else "orange" if a.get("dias_restantes") == 1 else "blue",
			}
		)

	for p in prazos or []:
		dias = p.get("dias_restantes", 99)
		urgencia = "red" if dias < 0 else "orange" if dias <= 3 else "yellow"
		items.append(
			{
				"type": "prazo",
				"sort_key": f"{p.get('due_date') or hoje} 12:00:00",
				"date": p.get("due_date"),
				"hora": "",
				"title": p.get("description") or p.get("name"),
				"subtitle": p.get("cliente_nome") or "",
				"detalhe": p.get("priority") or "",
				"doctype": "Deadline",
				"docname": p.get("name"),
				"urgencia": urgencia,
				"dias_restantes": dias,
			}
		)

	for t in tarefas or []:
		dias = t.get("dias_restantes")
		if t.get("due_date"):
			sort_key = f"{t.get('due_date')} 09:00:00"
			urgencia = "red" if dias is not None and dias < 0 else "orange" if dias == 0 else "yellow"
		else:
			sort_key = f"{hoje} 23:58:00"
			urgencia = "gray"
		items.append(
			{
				"type": "legal_task",
				"sort_key": sort_key,
				"date": t.get("due_date") or hoje,
				"hora": "",
				"title": t.get("subject") or t.get("name"),
				"subtitle": t.get("cliente_nome") or t.get("responsavel_nome") or "",
				"detalhe": t.get("status") or "",
				"doctype": "Legal Task",
				"docname": t.get("name"),
				"urgencia": urgencia,
				"dias_restantes": dias,
			}
		)

	items.sort(key=lambda x: x.get("sort_key") or "")
	return items
def _get_comunicacoes_pendentes(limit=LIST_LIMIT_MAX):
	if not frappe.has_permission("Case Communication", "read"):
		return []
	if not frappe.db.table_exists("Case Communication"):
		return []

	hoje = today()
	rows = frappe.get_all(
		"Case Communication",
		fields=[
			"name",
			"subject",
			"type",
			"client",
			"legal_case",
			"communication_date",
			"next_steps",
			"generate_task",
			"legal_task",
		],
		order_by="communication_date asc",
		limit_page_length=LIST_LIMIT_MAX,
	)
	servico_map = _servico_lookup([c.legal_case for c in rows if c.legal_case], ["client", "title"])
	cliente_nome_map = _cliente_nome_lookup(
		[c.client for c in rows if c.client]
		+ [sv.client for sv in servico_map.values() if sv.client]
	)

	tarefa_status_map = {
		row.name: row.status
		for row in frappe.get_all(
			"Legal Task",
			filters={"name": ["in", list({c.legal_task for c in rows if c.legal_task})]},
			fields=["name", "status"],
		)
	}

	pendentes = []
	for c in rows:
		dias = date_diff(hoje, getdate(c.communication_date)) if c.communication_date else 0
		motivo = ""
		urgencia = 2

		if c.next_steps and not c.legal_task:
			motivo = _("Aguardando follow-up")
			urgencia = 0
		elif c.legal_task:
			status_tarefa = tarefa_status_map.get(c.legal_task)
			if status_tarefa in ("Pendente", "Em Andamento"):
				motivo = _("Tarefa em aberto")
				urgencia = 1
			else:
				continue
		elif c.generate_task:
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
		c["cliente_nome"] = cliente_nome_map.get(c.client, c.client or "")
		sv = servico_map.get(c.legal_case) if c.legal_case else None
		c["servico_titulo"] = (sv.title if sv else "") or ""
		if not c["cliente_nome"] and sv and sv.client:
			c["cliente_nome"] = cliente_nome_map.get(sv.client, sv.client)
		pendentes.append(c)

	pendentes.sort(key=lambda x: (x.get("urgencia_ordem", 9), -x.get("dias_sem_retorno", 0)))
	return pendentes[: min(cint(limit or LIST_LIMIT_MAX), LIST_LIMIT_MAX)]
def _get_horas_periodo(hoje, periodo_fim):
	if not frappe.has_permission("Time Entry", "read"):
		return 0
	if not frappe.db.table_exists("Time Entry"):
		return 0
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(duration_hours), 0) as total
		FROM `tabTime Entry`
		WHERE entry_date BETWEEN %s AND %s
		""",
		(hoje, periodo_fim),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)
def _get_horas_semana(hoje):
	if not frappe.has_permission("Time Entry", "read"):
		return 0
	if not frappe.db.table_exists("Time Entry"):
		return 0
	week_start = add_days(hoje, -getdate(hoje).weekday())
	week_end = add_days(week_start, 6)
	result = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(duration_hours), 0) as total
		FROM `tabTime Entry`
		WHERE entry_date BETWEEN %s AND %s
		""",
		(week_start, week_end),
		as_dict=True,
	)
	return flt(result[0].total if result else 0)
def _get_tarefas(hoje, limit_start, limit):
	rows = frappe.get_all(
		"Legal Task",
		filters={"status": ["in", ["Pendente", "Em Andamento"]]},
		fields=["name", "subject", "status", "priority", "due_date", "legal_case", "responsible"],
		order_by="due_date asc, priority desc",
		limit_start=limit_start,
		limit_page_length=limit,
	)
	servico_map = _servico_lookup(
		[t.legal_case for t in rows if t.legal_case], ["client", "title"]
	)
	cliente_nome_map = _cliente_nome_lookup([sv.client for sv in servico_map.values() if sv.client])
	user_map = _user_nome_lookup([t.responsible for t in rows if t.responsible])
	for t in rows:
		if t.due_date:
			t["dias_restantes"] = date_diff(t.due_date, hoje)
		else:
			t["dias_restantes"] = None
		t["cliente_nome"] = ""
		t["servico_titulo"] = ""
		if t.legal_case:
			sv = servico_map.get(t.legal_case)
			if sv:
				t["cliente_nome"] = cliente_nome_map.get(sv.client, sv.client or "")
				t["servico_titulo"] = sv.title or ""
		t["responsavel_nome"] = user_map.get(t.responsible) if t.responsible else ""
	return rows
def _get_ultimas_comunicacoes(limit=5):
	if not frappe.has_permission("Case Communication", "read"):
		return []
	if not frappe.db.table_exists("Case Communication"):
		return []
	rows = frappe.get_all(
		"Case Communication",
		fields=["name", "subject", "type", "client", "legal_case", "communication_date"],
		order_by="communication_date DESC",
		limit=min(cint(limit or 5), LIST_LIMIT_MAX),
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
