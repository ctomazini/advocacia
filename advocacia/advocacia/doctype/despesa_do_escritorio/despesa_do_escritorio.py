import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class DespesadoEscritorio(Document):
	def validate(self):
		self._compor_titulo()
		self.atualizar_status()
		if self.recorrente and self.data_vencimento:
			self.calcular_proximo_vencimento()

	def after_insert(self):
		aplicar_titulo_pos_insert(self, usar_descricao=True)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self, usar_descricao=True)

	def atualizar_status(self):
		if self.status == "Cancelado":
			return
		if self.data_pagamento:
			self.status = "Pago"
		elif self.data_vencimento and getdate(self.data_vencimento) < getdate(today()):
			self.status = "Atrasado"

	def calcular_proximo_vencimento(self):
		meses = {
			"Mensal": 1,
			"Bimestral": 2,
			"Trimestral": 3,
			"Semestral": 6,
			"Anual": 12,
		}
		if self.frequencia and self.frequencia in meses:
			self.proximo_vencimento = add_months(
				getdate(self.data_vencimento), meses[self.frequencia]
			)


@frappe.whitelist()
def gerar_proxima_despesa(source_name: str) -> str:
	"""Cria nova despesa baseada na recorrente, com data de vencimento avançada."""
	frappe.has_permission("Despesa do Escritorio", "create", throw=True)
	source = frappe.get_doc("Despesa do Escritorio", source_name)
	if not source.recorrente or not source.proximo_vencimento:
		frappe.throw(
			_("Esta despesa não é recorrente ou não tem próximo vencimento calculado.")
		)

	nova = frappe.copy_doc(source)
	nova.data_vencimento = source.proximo_vencimento
	nova.data_pagamento = None
	nova.status = "Pendente"
	nova.comprovante = None
	nova.proximo_vencimento = None
	nova.insert()
	return nova.name
