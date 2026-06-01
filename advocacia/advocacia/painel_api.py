import frappe

from advocacia.advocacia.painel import get as _get_painel_data
from advocacia.advocacia.painel import financeiro as _painel_financeiro


@frappe.whitelist()
def get_painel_data(
	limit_start=0,
	limit_page_length=20,
	periodo_dias=7,
	list_limit=5,
	list_limits=None,
):
	return _get_painel_data(
		limit_start=limit_start,
		limit_page_length=limit_page_length,
		periodo_dias=periodo_dias,
		list_limit=list_limit,
		list_limits=list_limits,
	)


@frappe.whitelist()
def marcar_parcela_recebida(parcela_name):
	return _painel_financeiro.marcar_parcela(parcela_name)
