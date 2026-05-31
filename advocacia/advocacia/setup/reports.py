import json
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
	"produtividade/produtividade.json",
	"horas_por_servico/horas_por_servico.json",
)

_REPORT_SYNC_FIELDS = (
	"ref_doctype",
	"report_type",
	"module",
	"is_standard",
	"report_name",
	"disabled",
	"add_total_row",
)


def _load_report_json(path):
	with open(path) as f:
		return json.load(f)


def _import_report_json(path):
	"""Importa ou atualiza report a partir do JSON (sem deletar Standard Reports)."""
	data = _load_report_json(path)
	name = data.get("name")
	if not name:
		frappe.import_doc(path)
		return

	if frappe.db.exists("Report", name):
		doc = frappe.get_doc("Report", name)
		for field in _REPORT_SYNC_FIELDS:
			if field in data:
				doc.set(field, data[field])
		doc.save(ignore_permissions=True)
	else:
		frappe.import_doc(path)


def ensure_advocacia_reports():
	"""Sincroniza Script Reports do app (idempotente, sem deletar Standard Reports)."""
	for name in LEGACY_REPORT_NAMES:
		if not frappe.db.exists("Report", name):
			continue
		if frappe.db.get_value("Report", name, "is_standard") == "Yes":
			frappe.logger().info(
				"Report legado %s é Standard — mantido; versão ASCII importada separadamente.",
				name,
			)
			continue
		frappe.delete_doc("Report", name, force=True, ignore_permissions=True)

	base = frappe.get_app_path("advocacia", "advocacia", "report")
	for rel in REPORT_JSON_PATHS:
		path = os.path.join(base, rel)
		if os.path.exists(path):
			_import_report_json(path)

	frappe.clear_cache()
	frappe.db.commit()
