import frappe


ISTABLE_DOCTYPES = [
    "Fee Installment",
    "Legal Act Item",
    "Client Contact",
    "Client Address",
    "Document Kit Item",
]

PARENT_DOCTYPES_AFTER_ISTABLE = [
    "Document Kit",
]


def reinstalar_istable_doctypes():
    """Garante que DocTypes istable=1 existam no banco após migrate."""
    from frappe.modules.import_file import import_file_by_path
    import os

    base = frappe.get_app_path("advocacia", "advocacia", "doctype")
    reinstalados = []

    for dt in ISTABLE_DOCTYPES + PARENT_DOCTYPES_AFTER_ISTABLE:
        if not frappe.db.exists("DocType", dt):
            dt_path = os.path.join(base, frappe.scrub(dt), frappe.scrub(dt) + ".json")
            if os.path.exists(dt_path):
                import_file_by_path(dt_path, force=True)
                reinstalados.append(dt)

    if reinstalados:
        frappe.db.commit()
        frappe.logger().info(f"Reinstalados DocTypes: {reinstalados}")
