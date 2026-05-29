import frappe
from frappe import _
from frappe.model.document import Document


class Audiencia(Document):
	pass


@frappe.whitelist()
def get_events(start, end, filters=None, doctype=None, field_map=None, fields=None):
	"""Eventos do calendario para Audiencia."""
	if not frappe.has_permission("Audiencia", "read"):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	filter_list = [["data_hora", "between", [start, end]]]
	if filters:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
		if parsed:
			filter_list.extend(parsed)

	rows = frappe.get_all(
		"Audiencia",
		filters=filter_list,
		fields=[
			"name",
			"data_hora",
			"cliente",
			"tipo",
			"servico",
			"status_aud",
			"modalidade",
		],
		order_by="data_hora asc",
	)
	for row in rows:
		parts = [row.get("cliente") or "", row.get("tipo") or ""]
		row["title"] = " - ".join(p for p in parts if p) or row.name
	return rows
