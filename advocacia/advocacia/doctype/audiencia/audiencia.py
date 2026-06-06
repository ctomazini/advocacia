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
	"""Eventos do calendario para Audiencia."""
	frappe.has_permission("Audiencia", "read", throw=True)

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
