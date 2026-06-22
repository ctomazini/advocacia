import frappe
from frappe import _
from frappe.model.document import Document


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class Deadline(Document):
	def validate(self):
		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		if not self.client:
			frappe.throw(_("Client é obrigatório. Selecione um Processo válido."))
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)


@frappe.whitelist()
def get_events(
	start: str,
	end: str,
	filters=None,
	doctype: str | None = None,
	field_map=None,
	fields=None,
) -> list[dict]:
	"""Eventos do calendario para Deadline."""
	frappe.has_permission("Deadline", "read", throw=True)

	filter_list = [["due_date", "between", [start, end]]]
	if filters:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
		if parsed:
			filter_list.extend(parsed)

	return frappe.get_all(
		"Deadline",
		filters=filter_list,
		fields=[
			"name",
			"due_date",
			"description",
			"title",
			"client",
			"legal_case",
			"status",
			"priority",
		],
		order_by="due_date asc",
	)
