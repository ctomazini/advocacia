import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Pagamento(Document):
	def validate(self):
		if flt(self.valor) < 0:
			frappe.throw(frappe._("Valor não pode ser negativo."))
		if self.parcela_origem_id and not self.is_new():
			existing = frappe.db.get_value(
				"Pagamento",
				{"parcela_origem_id": self.parcela_origem_id, "name": ["!=", self.name]},
				"name",
			)
			if existing:
				frappe.throw(
					frappe._("Já existe pagamento para a parcela de origem {0}.").format(
						self.parcela_origem_id
					)
				)
