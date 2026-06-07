"""Renomeia coluna cobranca_id → pagamento na child table Ato Advocaticio."""
import frappe


def execute():
	doctype = "Ato Advocaticio"
	if not frappe.db.table_exists(doctype):
		return
	if frappe.db.has_column(doctype, "cobranca_id") and not frappe.db.has_column(
		doctype, "pagamento"
	):
		frappe.db.rename_column(doctype, "cobranca_id", "pagamento")
