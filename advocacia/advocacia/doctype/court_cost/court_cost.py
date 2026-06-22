import frappe
from frappe import _
from frappe.model.document import Document

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class CourtCost(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelado":
			frappe.throw(_("Custas canceladas não podem ser alteradas."))

		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		if not self.client:
			frappe.throw(_("Cliente é obrigatório. Selecione um Processo válido."))

		if self.payment_date and self.status == "Pendente":
			self.status = "Pago"
		if self.transfer_date and self.status == "Pago":
			self.status = "Repassado"
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)
