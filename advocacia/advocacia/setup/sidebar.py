import os

import frappe


def ensure_advocacia_sidebar():
	"""Garante Workspace Sidebar e Desktop Icon do app (sync idempotente)."""
	for folder, filename in (
		("workspace_sidebar", "Advocacia.json"),
		("desktop_icon", "Advocacia.json"),
	):
		path = frappe.get_app_path("advocacia", folder, filename)
		if os.path.exists(path):
			frappe.import_doc(path)
	frappe.db.commit()
