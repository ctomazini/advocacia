import frappe
from frappe import _
from frappe.model.document import Document


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class Audiencia(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		if not self.cliente:
			frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))
		recompor_titulo_se_vazio(self)

	def after_insert(self):
		aplicar_titulo_pos_insert(self)


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
