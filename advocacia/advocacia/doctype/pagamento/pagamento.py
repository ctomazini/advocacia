import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from advocacia.advocacia.financeiro import TIPO_ATOS, TIPO_HONORARIOS, is_pagamento_atos


class Pagamento(Document):
	def validate(self):
		if not self.tipo_origem:
			self.tipo_origem = TIPO_HONORARIOS

		if self.servico and not self.cliente:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")

		if self.tipo_origem == TIPO_HONORARIOS and not self.acordo:
			frappe.throw(
				_("Acordo é obrigatório para pagamentos de honorários."),
				title=_("Campo obrigatório"),
			)
		if self.tipo_origem == TIPO_ATOS and not self.registro_atos:
			frappe.throw(
				_("Registro de Atos é obrigatório para pagamentos de atos."),
				title=_("Campo obrigatório"),
			)

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
					_("Já existe pagamento para a origem {0}.").format(self.parcela_origem_id)
				)

	def before_save(self):
		if self.is_new() and self.status == "Cancelado":
			frappe.throw(_("Não é permitido criar pagamento já cancelado."))
		if is_pagamento_atos(self):
			self.manual_override = 0

	def on_trash(self):
		from advocacia.advocacia.financeiro import liberar_vinculos_pagamento_atos

		liberar_vinculos_pagamento_atos(self, revert_atos=True)
