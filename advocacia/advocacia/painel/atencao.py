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
		filters = [["status", "=", "Pendente"], ["data_prazo", "<", hoje]]
	else:
		filters = [["status", "=", "Pendente"], ["data_prazo", "between", [hoje, three_days]]]
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
	parcelas_vencidas = kpis.get("fee_installments_vencidas") or {"count": 0, "valor": 0}
	audiencias_hoje = cint(kpis.get("audiencias_hoje") or 0)
	audiencias_amanha = cint(kpis.get("audiencias_amanha") or 0)

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
					["data_limite", "<", hoje],
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
			meta_currency=flt(parcelas_vencidas.get("valor")),
			pulse=True,
		)
		if include_financial and cint(parcelas_vencidas.get("count") or 0)
		else None,
		_tile(
			audiencias_hoje + audiencias_amanha,
			"orange" if audiencias_hoje else "yellow",
			"gavel",
			_("Audiências"),
			{
				"doctype": "Hearing",
				"filters": [
					[
						"data_hora",
						"between",
						[
							f"{hoje} 00:00:00",
							f"{add_days(hoje, 1 if audiencias_amanha and not audiencias_hoje else 0)} 23:59:59",
						],
					],
				],
			},
			meta=_("{0} hoje · {1} amanhã").format(audiencias_hoje, audiencias_amanha),
			pulse=bool(audiencias_hoje),
		)
		if audiencias_hoje or audiencias_amanha
		else None,
	]

	tiles = [tile for tile in candidates if tile]
	return {
		"tiles": tiles,
		"all_clear": not tiles,
		"empty_label": _("Nada exige ação agora"),
		"ok_summary": _("Resto em dia ✓"),
	}
