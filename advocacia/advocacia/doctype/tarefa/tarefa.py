import frappe
from frappe.model.document import Document
from frappe.utils import today

from advocacia.advocacia.titulos import get_cliente_nome, join_title_parts


class Tarefa(Document):
	def validate(self):
		if self.servico and not self.cliente:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		self._compor_titulo()

	def _compor_titulo(self):
		if self.title:
			return
		cliente_nome = get_cliente_nome(self.cliente)
		titulo = (self.titulo or "").strip()
		self.title = join_title_parts(cliente_nome, titulo)

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
