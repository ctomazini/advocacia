import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class OfficeExpense(Document):
	def validate(self):
		self._compor_titulo()
		self.atualizar_status()
		if self.is_recurring and self.due_date:
			self.calcular_proximo_vencimento()

	def after_insert(self):
		aplicar_titulo_pos_insert(self, usar_descricao=True)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self, usar_descricao=True)

	def atualizar_status(self):
		if self.status == "Cancelado":
			return
		if self.payment_date:
			self.status = "Pago"
		elif self.due_date and getdate(self.due_date) < getdate(today()):
			self.status = "Atrasado"

	def calcular_proximo_vencimento(self):
		meses = {
			"Mensal": 1,
			"Bimestral": 2,
			"Trimestral": 3,
			"Semestral": 6,
			"Anual": 12,
		}
		if self.frequency and self.frequency in meses:
			self.next_due_date = add_months(
				getdate(self.due_date), meses[self.frequency]
			)


@frappe.whitelist()
def gerar_proxima_despesa(source_name: str) -> str:
	"""Cria nova despesa baseada na recorrente, com data de vencimento avançada."""
	frappe.has_permission("Office Expense", "create", throw=True)
	source = frappe.get_doc("Office Expense", source_name)
	if not source.is_recurring or not source.next_due_date:
		frappe.throw(
			_("Esta despesa não é recorrente ou não tem próximo vencimento calculado.")
		)

	nova = frappe.copy_doc(source)
	nova.due_date = source.next_due_date
	nova.payment_date = None
	nova.status = "Pendente"
	nova.receipt = None
	nova.next_due_date = None
	nova.insert()
	return nova.name
