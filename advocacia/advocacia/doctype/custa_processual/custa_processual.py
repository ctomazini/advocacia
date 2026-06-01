import frappe
from frappe import _
from frappe.model.document import Document

from advocacia.advocacia.titulos import fmt_date, get_cliente_nome, join_context_parts, join_title_parts


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
		self._compor_titulo()

	def _compor_titulo(self):
		if self.title:
			return
		cliente_nome = get_cliente_nome(self.cliente)
		contexto = join_context_parts(self.tipo, fmt_date(self.data_pagamento))
		self.title = join_title_parts(cliente_nome, contexto)
