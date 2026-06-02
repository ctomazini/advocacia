import frappe
from frappe.model.document import Document
from frappe.utils import today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class Tarefa(Document):
	def validate(self):
		if self.servico and not self.cliente:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		recompor_titulo_se_vazio(self)

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def before_save(self):
		if self.status == "Concluída" and not self.data_conclusao:
			self.data_conclusao = today()

	@frappe.whitelist()
	def concluir(self):
		self.check_permission("write")
		self.status = "Concluída"
		self.data_conclusao = today()
		self.save()
		return {"status": self.status}
