import os

import frappe

PRINT_FORMAT_NAMES = (
	"Advocacia - Recibo de Honorários",
	"Advocacia - Resumo do Processo",
	"Advocacia - Contrato de Honorários",
)

_PRINT_FORMATS = (
	{
		"name": "Advocacia - Recibo de Honorários",
		"doc_type": "Legal Payment",
		"html_file": "recibo_honorarios.html",
	},
	{
		"name": "Advocacia - Resumo do Processo",
		"doc_type": "Legal Case",
		"html_file": "resumo_processo.html",
	},
	{
		"name": "Advocacia - Contrato de Honorários",
		"doc_type": "Fee Agreement",
		"html_file": "contrato_honorarios.html",
	},
)

_SYNC_FIELDS = (
	"print_format_for",
	"doc_type",
	"module",
	"standard",
	"custom_format",
	"print_format_type",
	"disabled",
	"html",
)


def _load_html(filename):
	base = frappe.get_app_path("advocacia", "print_formats")
	path = os.path.join(base, filename)
	with open(path, encoding="utf-8") as f:
		return f.read()


def _sync_print_format(spec):
	html = _load_html(spec["html_file"])
	values = {
		"print_format_for": "DocType",
		"doc_type": spec["doc_type"],
		"module": "Advocacia",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "Jinja",
		"disabled": 0,
		"html": html,
	}

	if frappe.db.exists("Print Format", spec["name"]):
		doc = frappe.get_doc("Print Format", spec["name"])
		for field in _SYNC_FIELDS:
			doc.set(field, values[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza print formats do app
	else:
		doc = frappe.get_doc({"doctype": "Print Format", "name": spec["name"], **values})
		doc.insert(ignore_permissions=True)  # setup: sincroniza print formats do app


def ensure_advocacia_print_formats():
	"""Sincroniza Print Formats do app (idempotente)."""
	for spec in _PRINT_FORMATS:
		_sync_print_format(spec)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza print formats no migrate
