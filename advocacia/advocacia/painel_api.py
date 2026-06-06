import frappe

from advocacia.advocacia.painel import get as _get_painel_data
from advocacia.advocacia.painel import financeiro as _painel_financeiro


@frappe.whitelist()
def get_painel_data(
	limit_start: int = 0,
	limit_page_length: int = 20,
	periodo_dias: int = 7,
	list_limit: int = 5,
	list_limits: dict | str | None = None,
) -> dict:
	"""Return dashboard payload for the current user."""
	frappe.has_permission("Servico", "read", throw=True)
	return _get_painel_data(
		limit_start=limit_start,
		limit_page_length=limit_page_length,
		periodo_dias=periodo_dias,
		list_limit=list_limit,
		list_limits=list_limits,
	)


@frappe.whitelist()
def marcar_parcela_recebida(parcela_name: str) -> dict:
	"""Mark a Pagamento (or legacy parcel row) as received."""
	frappe.has_permission("Pagamento", "write", throw=True)
	return _painel_financeiro.marcar_parcela(parcela_name)
