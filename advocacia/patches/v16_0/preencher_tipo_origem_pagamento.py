import frappe

from advocacia.advocacia.financeiro import TIPO_HONORARIOS


def execute():
	"""Preenche tipo_origem em Pagamentos existentes (pré P9b)."""
	frappe.db.sql(
		"""
		UPDATE `tabPagamento`
		SET tipo_origem = %s
		WHERE IFNULL(tipo_origem, '') = ''
		""",
		TIPO_HONORARIOS,
	)
	frappe.db.commit()
