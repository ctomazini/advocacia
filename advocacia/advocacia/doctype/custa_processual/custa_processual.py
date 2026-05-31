import frappe
from frappe import _
from frappe.model.document import Document


class CustaProcessual(Document):
	def validate(self):
		if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "status") == "Cancelado":
			frappe.throw(_("Custas canceladas não podem ser alteradas."))

		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		if not self.cliente:
			frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))

		if self.data_pagamento and self.status == "Pendente":
			self.status = "Pago"
		if self.data_repasse and self.status == "Pago":
			self.status = "Repassado"
