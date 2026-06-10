import os

import frappe

PRINT_FORMAT_NAMES = (
	"Advocacia - Recibo de Honorários",
	"Advocacia - Resumo do Processo",
	"Advocacia - Contrato de Honorários",
	"Advocacia - Inadimplência",
	"Advocacia - Fluxo de Caixa",
	"Advocacia - Honorários por Cliente",
	"Advocacia - Carteira Ativa",
	"Advocacia - Carteira Ativa (Paisagem)",
	"Advocacia - Produtividade",
	"Advocacia - Produtividade (Paisagem)",
	"Advocacia - Horas por Serviço",
	"Advocacia - Horas por Serviço (Paisagem)",
)

_DOCTYPE_PRINT_FORMATS = (
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

_REPORT_PRINT_FORMATS = (
	{
		"name": "Advocacia - Inadimplência",
		"report": "inadimplencia",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Fluxo de Caixa",
		"report": "fluxo_de_caixa",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Honorários por Cliente",
		"report": "honorarios_por_cliente",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Carteira Ativa",
		"report": "carteira_ativa",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Carteira Ativa (Paisagem)",
		"report": "carteira_ativa",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
	{
		"name": "Advocacia - Produtividade",
		"report": "produtividade",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Produtividade (Paisagem)",
		"report": "produtividade",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
	{
		"name": "Advocacia - Horas por Serviço",
		"report": "horas_por_servico",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
	},
	{
		"name": "Advocacia - Horas por Serviço (Paisagem)",
		"report": "horas_por_servico",
		"parts": ("reports/_header.html", "reports/_table_all.html", "reports/_footer.html"),
		"landscape": True,
	},
)

_DOCTYPE_SYNC_FIELDS = (
	"print_format_for",
	"doc_type",
	"module",
	"standard",
	"custom_format",
	"print_format_type",
	"disabled",
	"html",
)

_REPORT_SYNC_FIELDS = (
	"print_format_for",
	"report",
	"module",
	"standard",
	"custom_format",
	"print_format_type",
	"disabled",
	"html",
	"css",
)


def _load_html(filename):
	base = frappe.get_app_path("advocacia", "print_formats")
	path = os.path.join(base, filename)
	with open(path, encoding="utf-8") as f:
		return f.read()


def _compose_report_html(parts, landscape=False):
	sections = [_load_html("reports/_styles.html")]
	if landscape:
		sections.append(_load_html("reports/_landscape.css"))
	for part in parts:
		sections.append(_load_html(part))
	return "\n".join(sections)


def _sync_doctype_print_format(spec):
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
		for field in _DOCTYPE_SYNC_FIELDS:
			doc.set(field, values[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza print formats do app
	else:
		doc = frappe.get_doc({"doctype": "Print Format", "name": spec["name"], **values})
		doc.insert(ignore_permissions=True)  # setup: sincroniza print formats do app


def _sync_report_print_format(spec):
	html = _compose_report_html(spec.get("parts") or (), spec.get("landscape"))
	values = {
		"print_format_for": "Report",
		"report": spec["report"],
		"module": "Advocacia",
		"standard": "No",
		"custom_format": 1,
		"print_format_type": "JS",
		"disabled": 0,
		"html": html,
		"css": None,
	}

	if frappe.db.exists("Print Format", spec["name"]):
		doc = frappe.get_doc("Print Format", spec["name"])
		for field in _REPORT_SYNC_FIELDS:
			doc.set(field, values[field])
		doc.save(ignore_permissions=True)  # setup: sincroniza print formats do app
	else:
		doc = frappe.get_doc({"doctype": "Print Format", "name": spec["name"], **values})
		doc.insert(ignore_permissions=True)  # setup: sincroniza print formats do app


def ensure_advocacia_print_formats():
	"""Sincroniza Print Formats do app (DocType + Script Reports, idempotente)."""
	for spec in _DOCTYPE_PRINT_FORMATS:
		_sync_doctype_print_format(spec)
	for spec in _REPORT_PRINT_FORMATS:
		_sync_report_print_format(spec)

	frappe.clear_cache()
	frappe.db.commit()  # setup: sincroniza print formats no migrate
