import os

import frappe

LEGACY_REPORT_NAMES = (
	"Inadimplência",
	"Fluxo de Caixa Projetado",
	"Honorários por Cliente",
	"Carteira Ativa",
)

REPORT_JSON_PATHS = (
	"inadimplencia/inadimplencia.json",
	"fluxo_de_caixa/fluxo_de_caixa.json",
	"honorarios_por_cliente/honorarios_por_cliente.json",
	"carteira_ativa/carteira_ativa.json",
)


def ensure_advocacia_reports():
	"""Remove relatórios com nome acentuado e reimporta paths ASCII (idempotente)."""
	for name in LEGACY_REPORT_NAMES:
		if frappe.db.exists("Report", name):
			frappe.delete_doc("Report", name, force=True, ignore_permissions=True)

	base = frappe.get_app_path("advocacia", "advocacia", "report")
	for rel in REPORT_JSON_PATHS:
		path = os.path.join(base, rel)
		if os.path.exists(path):
			frappe.import_doc(path)

	frappe.clear_cache()
	frappe.db.commit()
