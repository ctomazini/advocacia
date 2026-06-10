from frappe import _
from frappe.utils import add_days, date_diff


def _relative_when(hoje, date_value):
	if not date_value:
		return _("Sem data")
	dias = date_diff(date_value, hoje)
	if dias == 0:
		return _("Hoje")
	if dias == 1:
		return _("Amanhã")
	if dias == -1:
		return _("Ontem")
	if dias < 0:
		return _("Há {0} dias").format(abs(dias))
	return _("Em {0} dias").format(dias)


def _icon_for_tipo(tipo):
	return {
		"prazo": "clock-alert",
		"audiencia": "gavel",
		"legal_task": "list-todo",
	}.get(tipo, "calendar")


def build_agenda_dias(hoje, periodo_dias, timeline_items):
	days = []
	for offset in range(min(periodo_dias, 7)):
		day = add_days(hoje, offset)
		day_items = [row for row in timeline_items if row.get("date") == day]
		days.append(
			{
				"date": day,
				"label": _relative_when(hoje, day),
				"count": len(day_items),
				"tone": "red"
				if any(row.get("urgencia") == "red" for row in day_items)
				else "orange"
				if day_items
				else "gray",
			}
		)
	return days


def build_proximo_evento(timeline_items, hoje=None, limit=2):
	if hoje is None:
		from frappe.utils import today

		hoje = today()
	items = sorted(timeline_items or [], key=lambda row: row.get("sort_key") or "")
	upcoming = []
	for item in items:
		if item.get("type") == "pagamento":
			continue
		enriched = dict(item)
		enriched["when_label"] = _relative_when(hoje, item.get("date"))
		enriched["icon"] = _icon_for_tipo(item.get("type"))
		enriched["type"] = item.get("type")
		upcoming.append(enriched)
		if len(upcoming) >= limit:
			break
	return upcoming
