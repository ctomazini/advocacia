import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from advocacia.advocacia.setup.translations import ensure_doctype_translations
from advocacia.advocacia.setup.sidebar import ensure_advocacia_sidebar
from advocacia.advocacia.setup.reports import ensure_advocacia_reports


def _ensure_event_custom_fields():
	create_custom_field(
		"Event",
		{
			"fieldname": "custom_source_doctype",
			"label": "Source DocType",
			"fieldtype": "Data",
			"hidden": 1,
			"no_copy": 1,
		},
	)
	create_custom_field(
		"Event",
		{
			"fieldname": "custom_source_name",
			"label": "Source Name",
			"fieldtype": "Data",
			"hidden": 1,
			"no_copy": 1,
		},
	)


def ensure_event_custom_fields():
	"""Idempotente — usado em after_install e after_migrate."""
	_ensure_event_custom_fields()
	frappe.clear_cache(doctype="Event")


def after_install():
	for role in ["Advocacia User", "Advocacia Manager"]:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "is_custom": 1}).insert(
				ignore_permissions=True  # setup: cria roles durante install como Administrator
			)
	ensure_event_custom_fields()
	ensure_doctype_translations()
	ensure_advocacia_sidebar()
	ensure_advocacia_reports()
	frappe.db.commit()
