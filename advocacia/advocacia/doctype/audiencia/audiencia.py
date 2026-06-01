import frappe
from frappe import _
from frappe.model.document import Document


class Audiencia(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		if not self.cliente:
			frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))
		self.compor_titulo()

	def compor_titulo(self):
		cliente_label = ""
		if self.cliente:
			cliente_label = frappe.db.get_value("Cliente", self.cliente, "nome") or self.cliente
		base = self.tipo or _("Audiência")
		self.title = f"{cliente_label} — {base}" if cliente_label else base


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
			"title",
			"servico",
			"status_aud",
			"modalidade",
		],
		order_by="data_hora asc",
	)
	for row in rows:
		row["title"] = row.get("title") or row.get("tipo") or row.name
	return rows
