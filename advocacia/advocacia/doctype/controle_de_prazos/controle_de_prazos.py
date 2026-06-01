import frappe
from frappe import _
from frappe.model.document import Document


from advocacia.advocacia.titulos import fmt_date, get_cliente_nome, join_context_parts, join_title_parts


class ControledePrazos(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		if not self.cliente:
			frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))
		self._compor_titulo()

	def _compor_titulo(self):
		if self.title:
			return
		cliente_nome = get_cliente_nome(self.cliente)
		descricao = (self.descricao or "").strip() or "Prazo"
		contexto = join_context_parts(descricao, fmt_date(self.data_prazo))
		self.title = join_title_parts(cliente_nome, contexto)


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
