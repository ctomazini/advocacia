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
	"fee_installments",
	"despesas",
	"custas",
)
def _nomes_lookup(doctype, names, campo_nome):
	"""Retorna dict {name: nome_legivel} para uma lista de IDs."""
	names = list({name for name in names if name})
	if not names:
		return {}
	rows = frappe.get_all(doctype, filters={"name": ["in", names]}, fields=["name", campo_nome])
	return {row.name: row.get(campo_nome) or row.name for row in rows}

def _cliente_nome_lookup(cliente_names):
	return _nomes_lookup("Client", cliente_names, "client_name")
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
	rows = frappe.get_all("Legal Case", filters={"name": ["in", names]}, fields=fields)
	return {row.name: row for row in rows}
def _user_nome_lookup(user_names):
	names = list({name for name in user_names if name})
	if not names:
		return {}
	rows = frappe.get_all("User", filters={"name": ["in", names]}, fields=["name", "full_name"])
	return {row.name: row.full_name or row.name for row in rows}


def user_is_advocacia_manager() -> bool:
	"""True se o usuário atual tem role Advocacia Manager."""
	return "Advocacia Manager" in frappe.get_roles()


_KPIS_FINANCIAL_KEYS = (
	"fee_installments_vencidas",
	"fee_installments_a_vencer_30d",
	"recebido_mes",
	"recebido_periodo",
	"recebido_hoje",
	"previsto_mes",
	"honorarios_ativos",
	"custas_abertas",
	"taxa_recebimento",
)

_RESUMO_FINANCIAL_KEYS = (
	"fee_installments_vencidas",
	"previsto_periodo_valor",
	"previsto_semana_valor",
)


def strip_financial_payload(data: dict) -> dict:
	"""Remove dados financeiros do payload do painel para Advocacia User."""
	if user_is_advocacia_manager():
		return data

	for key in (
		"financeiro",
		"fee_installments",
		"despesas_pendentes",
		"total_despesas_mes",
		"custas_pendentes_repasse",
		"total_custas_mes",
	):
		data.pop(key, None)

	kpis = data.get("kpis")
	if isinstance(kpis, dict):
		for key in _KPIS_FINANCIAL_KEYS:
			kpis.pop(key, None)

	resumo = data.get("summary")
	if isinstance(resumo, dict):
		for key in _RESUMO_FINANCIAL_KEYS:
			resumo.pop(key, None)

	list_meta = data.get("list_meta")
	if isinstance(list_meta, dict):
		for key in ("fee_installments", "despesas", "custas"):
			list_meta.pop(key, None)

	return data
