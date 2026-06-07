"""Renomeia coluna cobranca_id → pagamento na child table Legal Act Item."""
import frappe


def execute():
	doctype = "Legal Act Item"
	if not frappe.db.table_exists(doctype):
		return
	if frappe.db.has_column(doctype, "cobranca_id") and not frappe.db.has_column(
		doctype, "payment"
	):
		frappe.db.rename_column(doctype, "cobranca_id", "payment")
