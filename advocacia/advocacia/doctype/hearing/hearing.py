import frappe
from frappe import _
from frappe.model.document import Document


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class Hearing(Document):
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
	"""Eventos do calendario para Hearing."""
	frappe.has_permission("Hearing", "read", throw=True)

	filter_list = [["hearing_datetime", "between", [start, end]]]
	if filters:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
		if parsed:
			filter_list.extend(parsed)

	rows = frappe.get_all(
		"Hearing",
		filters=filter_list,
		fields=[
			"name",
			"hearing_datetime",
			"client",
			"type",
			"title",
			"legal_case",
			"status",
			"modality",
		],
		order_by="hearing_datetime asc",
	)
	for row in rows:
		row["title"] = row.get("title") or row.get("type") or row.name
	return rows
