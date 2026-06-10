import frappe

from advocacia.advocacia.financeiro import TIPO_HONORARIOS


def execute():
	"""Preenche tipo_origem em Legal Payments existentes (pré P9b)."""
	frappe.db.sql(
		"""
		UPDATE `tabLegal Payment`
		SET origin_type = %s
		WHERE IFNULL(origin_type, '') = ''
		""",
		TIPO_HONORARIOS,
	)
	frappe.db.commit()
