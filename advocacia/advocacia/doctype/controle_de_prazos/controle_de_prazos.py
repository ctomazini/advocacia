import frappe
from frappe import _
from frappe.model.document import Document


class ControledePrazos(Document):
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
		descricao = (self.descricao or "").strip() or "Prazo"
		self.title = f"{cliente_label} — {descricao}" if cliente_label else descricao


@frappe.whitelist()
def get_events(start, end, filters=None, doctype=None, field_map=None, fields=None):
	"""Eventos do calendario para Controle de Prazos."""
	if not frappe.has_permission("Controle de Prazos", "read"):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	filter_list = [["data_prazo", "between", [start, end]]]
	if filters:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
		if parsed:
			filter_list.extend(parsed)

	return frappe.get_all(
		"Controle de Prazos",
		filters=filter_list,
		fields=[
			"name",
			"data_prazo",
			"descricao",
			"title",
			"cliente",
			"servico",
			"status",
			"prioridade",
		],
		order_by="data_prazo asc",
	)
