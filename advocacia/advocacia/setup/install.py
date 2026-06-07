import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from advocacia.advocacia.setup.permissions import setup_permissions
from advocacia.advocacia.setup.reports import ensure_advocacia_reports
from advocacia.advocacia.setup.roles import create_roles
from advocacia.advocacia.setup.sidebar import ensure_advocacia_sidebar
from advocacia.advocacia.setup.translations import ensure_doctype_translations


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


def ensure_office_settings():
	"""Seed idempotente do Single de configuração do escritório."""
	if frappe.db.exists("Office Settings", "Office Settings"):
		return
	frappe.get_doc(
		{
			"doctype": "Office Settings",
			"razao_social": "Escritório de Advocacia",
			"advogada": "Advogada(o) Responsável",
			"oab": "000000",
			"endereco": "Endereço profissional do escritório",
			"default_notify_days": 3,
		}
	).insert(ignore_permissions=True)  # setup: seed do Single de configuração


def after_install():
	create_roles()
	setup_permissions()
	ensure_event_custom_fields()
	ensure_doctype_translations()
	ensure_advocacia_sidebar()
	ensure_advocacia_reports()
	ensure_office_settings()
	frappe.db.commit()
