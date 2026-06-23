import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from advocacia.advocacia.financeiro import (
	TIPO_ATOS,
	TIPO_HONORARIOS,
	effective_open_status,
	is_pagamento_atos,
)
from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class LegalPayment(Document):
	def validate(self):
		if not self.origin_type:
			self.origin_type = TIPO_HONORARIOS

		if self.legal_case and not self.client:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")

		if self.origin_type == TIPO_HONORARIOS and not self.fee_agreement:
			frappe.throw(
				_("Acordo é obrigatório para recebimentos de honorários."),
				title=_("Campo obrigatório"),
			)
		if self.origin_type == TIPO_ATOS and not self.service_record:
			frappe.throw(
				_("Cobrança Individual é obrigatória para recebimentos de atos."),
				title=_("Campo obrigatório"),
			)

		if flt(self.amount) < 0:
			frappe.throw(_("Valor não pode ser negativo."))

		if not self.is_new() and self.name:
			old_status = frappe.db.get_value(self.doctype, self.name, "status")
			if old_status == "Cancelado":
				frappe.throw(
					_("Recebimento cancelado não pode ser alterado. Exclua o registro se necessário."),
					title=_("Registro imutável"),
				)

		if self.installment_origin_id and not self.is_new():
			existing = frappe.db.get_value(
				"Legal Payment",
				{"installment_origin_id": self.installment_origin_id, "name": ["!=", self.name]},
				"name",
			)
			if existing:
				frappe.throw(
					_("Já existe recebimento para a origem {0}.").format(self.installment_origin_id)
				)

		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def before_save(self):
		if self.is_new() and self.status == "Cancelado":
			frappe.throw(_("Não é permitido criar recebimento já cancelado."))
		if is_pagamento_atos(self):
			self.manual_override = 0
		if not self.manual_override and self.status in ("Pendente", "Vencido"):
			self.status = effective_open_status(self.status, self.due_date)

	def on_trash(self):
		from advocacia.advocacia.financeiro import liberar_vinculos_pagamento_atos

		liberar_vinculos_pagamento_atos(self, revert_atos=True)
