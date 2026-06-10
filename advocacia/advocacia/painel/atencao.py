from frappe import _
from frappe.utils import add_days, cint, flt


def _tile(count, tone, icon, label, deep_link, meta=None, meta_currency=None, pulse=False):
	return {
		"count": cint(count),
		"tone": tone,
		"icon": icon,
		"label": label,
		"deep_link": deep_link,
		"meta": meta,
		"meta_currency": meta_currency,
		"pulse": bool(pulse and cint(count)),
	}


def _prazos_tile(overdue, urgent, hoje, three_days):
	total = cint(overdue) + cint(urgent)
	if not total:
		return None
	meta = _("{0} vencidos · {1} em 3 dias").format(cint(overdue), cint(urgent))
	tone = "red" if overdue else "orange"
	if overdue:
		filters = [["status", "=", "Pendente"], ["due_date", "<", hoje]]
	else:
		filters = [["status", "=", "Pendente"], ["due_date", "between", [hoje, three_days]]]
	return _tile(
		total,
		tone,
		"alarm-clock",
		_("Prazos"),
		{"doctype": "Deadline", "filters": filters},
		meta=meta,
		pulse=True,
	)


def build_attention_tiles(hoje, kpis, financeiro, include_financial=True):
	del financeiro
	three_days = add_days(hoje, 3)
	overdue_deadlines = cint(kpis.get("prazos_vencidos") or 0)
	urgent_deadlines = cint(kpis.get("prazos_criticos") or 0)
	late_tasks = cint(kpis.get("legal_tasks_atrasadas") or 0)
	parcelas_vencidas = kpis.get("fee_installments_vencidas") or {"count": 0, "amount": 0}
	audiencias_hoje = cint(kpis.get("audiencias_hoje") or 0)
	audiencias_amanha = cint(kpis.get("audiencias_amanha") or 0)
	amanha = add_days(hoje, 1)

	candidates = [
		_prazos_tile(overdue_deadlines, urgent_deadlines, hoje, three_days),
		_tile(
			late_tasks,
			"orange",
			"list-todo",
			_("Tarefas atrasadas"),
			{
				"doctype": "Legal Task",
				"filters": [
					["status", "in", ["Pendente", "Em Andamento"]],
					["due_date", "<", hoje],
				],
			},
			pulse=True,
		)
		if late_tasks
		else None,
		_tile(
			parcelas_vencidas.get("count") or 0,
			"red",
			"circle-dollar-sign",
			_("Parcelas vencidas"),
			{"doctype": "Legal Payment", "filters": [["status", "=", "Vencido"]]},
			meta_currency=flt(parcelas_vencidas.get("amount")),
			pulse=True,
		)
		if include_financial and cint(parcelas_vencidas.get("count") or 0)
		else None,
		_tile(
			audiencias_hoje,
			"orange",
			"gavel",
			_("Audiências hoje"),
			{
				"doctype": "Hearing",
				"filters": [
					["hearing_datetime", "between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]],
				],
			},
			pulse=True,
		)
		if audiencias_hoje
		else None,
		_tile(
			audiencias_amanha,
			"yellow",
			"gavel",
			_("Audiências amanhã"),
			{
				"doctype": "Hearing",
				"filters": [
					["hearing_datetime", "between", [f"{amanha} 00:00:00", f"{amanha} 23:59:59"]],
				],
			},
		)
		if audiencias_amanha
		else None,
	]

	tiles = [tile for tile in candidates if tile]
	return {
		"tiles": tiles,
		"all_clear": not tiles,
		"empty_label": _("Nada exige ação agora"),
	}
