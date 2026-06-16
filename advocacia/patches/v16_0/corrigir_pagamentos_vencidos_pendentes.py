import frappe


def execute():
	"""Corrige pagamentos/parcelas pendentes com vencimento no passado (produção)."""
	from advocacia.advocacia.tasks import verificar_parcelas_vencidas

	verificar_parcelas_vencidas()
	frappe.db.commit()
