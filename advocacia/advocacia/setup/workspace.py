import os

import frappe


def ensure_advocacia_workspace():
	"""Sincroniza o Workspace Advocacia a partir do JSON do módulo (idempotente)."""
	path = frappe.get_app_path(
		"advocacia",
		"advocacia",
		"workspace",
		"advocacia",
		"advocacia.json",
	)
	if os.path.exists(path):
		frappe.import_doc(path)
	frappe.clear_cache()
	frappe.db.commit()
