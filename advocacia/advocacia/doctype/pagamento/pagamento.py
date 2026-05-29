import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Pagamento(Document):
	def validate(self):
		if flt(self.valor) < 0:
			frappe.throw(_("Valor não pode ser negativo."))

		if not self.is_new() and self.name:
			old_status = frappe.db.get_value(self.doctype, self.name, "status")
			if old_status == "Cancelado":
				frappe.throw(
					_("Pagamento cancelado não pode ser alterado. Exclua o registro se necessário."),
					title=_("Registro imutável"),
				)

		if self.parcela_origem_id and not self.is_new():
			existing = frappe.db.get_value(
				"Pagamento",
				{"parcela_origem_id": self.parcela_origem_id, "name": ["!=", self.name]},
				"name",
			)
			if existing:
				frappe.throw(
					_("Já existe pagamento para a parcela de origem {0}.").format(
						self.parcela_origem_id
					)
				)

	def before_save(self):
		if self.is_new() and self.status == "Cancelado":
			frappe.throw(_("Não é permitido criar pagamento já cancelado."))
