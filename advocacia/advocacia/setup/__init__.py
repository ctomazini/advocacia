import frappe


ISTABLE_DOCTYPES = [
    "Parcela de Honorarios",
    "Ato Advocaticio",
    "Contato Cliente",
    "Endereco Cliente",
    "Kit Documento Item",
]

PARENT_DOCTYPES_AFTER_ISTABLE = [
    "Kit de Documentos",
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
