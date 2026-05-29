import frappe

from advocacia.advocacia.setup.translations import ensure_doctype_translations
from advocacia.advocacia.setup.sidebar import ensure_advocacia_sidebar


def after_install():
	for role in ["Advocacia User", "Advocacia Manager"]:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "is_custom": 1}).insert(
				ignore_permissions=True
			)
	ensure_doctype_translations()
	ensure_advocacia_sidebar()
	frappe.db.commit()
