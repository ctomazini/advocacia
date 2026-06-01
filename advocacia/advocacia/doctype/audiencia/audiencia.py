import frappe
from frappe import _
from frappe.model.document import Document


from advocacia.advocacia.titulos import fmt_datetime, get_cliente_nome, join_context_parts, join_title_parts


class Audiencia(Document):
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
		contexto = join_context_parts(self.tipo or _("Audiência"), fmt_datetime(self.data_hora))
		self.title = join_title_parts(cliente_nome, contexto)


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
