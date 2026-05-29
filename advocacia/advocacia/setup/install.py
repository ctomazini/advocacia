import frappe


def after_install():
    for role in ["Advocacia User", "Advocacia Manager"]:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "is_custom": 1}).insert(ignore_permissions=True)
    frappe.db.commit()
