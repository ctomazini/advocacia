"""Seed idempotente de cadastros universais (produção)."""

import frappe

DEFAULT_CASE_PHASES = (
	{"case_phase_name": "Distribuído", "sort_order": 10},
	{"case_phase_name": "Em andamento", "sort_order": 20},
	{"case_phase_name": "Sentenciado", "sort_order": 30},
	{"case_phase_name": "Recursal", "sort_order": 40},
	{"case_phase_name": "Arquivado", "sort_order": 50},
)


def _ensure_case_phase(phase_def):
	name = phase_def["case_phase_name"]
	if frappe.db.exists("Case Phase", name):
		doc = frappe.get_doc("Case Phase", name)
		if doc.sort_order != phase_def["sort_order"]:
			doc.sort_order = phase_def["sort_order"]
			doc.save(ignore_permissions=True)  # setup: seed idempotente
		return

	frappe.get_doc(
		{
			"doctype": "Case Phase",
			"case_phase_name": name,
			"sort_order": phase_def["sort_order"],
		}
	).insert(ignore_permissions=True)  # setup: seed idempotente


def ensure_seed_data():
	"""Cadastros auxiliares universais — idempotente no migrate."""
	for phase_def in DEFAULT_CASE_PHASES:
		_ensure_case_phase(phase_def)

	frappe.db.commit()  # setup: seed idempotente no migrate
