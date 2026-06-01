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

LIST_LIMIT_MAX = 100
DEFAULT_LIST_LIMIT_KEYS = (
	"timeline",
	"comunicacoes",
	"parcelas",
	"despesas",
	"custas",
)
def _cliente_nome_lookup(cliente_names):
	names = list({name for name in cliente_names if name})
	if not names:
		return {}
	rows = frappe.get_all("Cliente", filters={"name": ["in", names]}, fields=["name", "nome"])
	return {row.name: row.nome or row.name for row in rows}
def _effective_list_cap(list_limit):
	if not list_limit:
		return LIST_LIMIT_MAX
	return list_limit
def _list_cap(list_limits, key):
	return _effective_list_cap(list_limits.get(key, 5))
def _normalize_list_limit(list_limit):
	val = cint(list_limit if list_limit is not None else 5)
	if val == 0:
		return 0
	if val not in (5, 10, 15):
		return 5
	return val
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
def _normalize_periodo_dias(periodo_dias):
	dias = cint(periodo_dias or 7)
	if dias not in (1, 7, 15, 30):
		dias = 7
	return dias
def _servico_lookup(servico_names, extra_fields):
	names = list({name for name in servico_names if name})
	if not names:
		return {}
	fields = ["name"] + [f for f in extra_fields if f != "name"]
	rows = frappe.get_all("Servico", filters={"name": ["in", names]}, fields=fields)
	return {row.name: row for row in rows}
def _user_nome_lookup(user_names):
	names = list({name for name in user_names if name})
	if not names:
		return {}
	rows = frappe.get_all("User", filters={"name": ["in", names]}, fields=["name", "full_name"])
	return {row.name: row.full_name or row.name for row in rows}
