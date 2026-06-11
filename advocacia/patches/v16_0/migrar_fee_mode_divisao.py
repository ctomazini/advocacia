"""Renomeia fee_mode legado Acordo com Divisão → Divisão advogada/cliente."""

import frappe


def execute():
	frappe.db.sql(
		"""
		UPDATE `tabFee Agreement`
		SET fee_mode = 'Divisão advogada/cliente'
		WHERE fee_mode = 'Acordo com Divisão'
		"""
	)
