import frappe
from frappe.model.document import Document
from frappe import _


class Comunicacao(Document):
	def validate(self):
		if not self.tipo:
			frappe.throw(_("Tipo é obrigatório."))
		if self.servico and not self.cliente:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")

	def after_insert(self):
		if self.gerar_tarefa and self.proximos_passos:
			tarefa = frappe.get_doc(
				{
					"doctype": "Tarefa",
					"titulo": f"Follow-up: {self.assunto}",
					"descricao": self.proximos_passos,
					"servico": self.servico,
					"status": "Pendente",
				}
			)
			tarefa.insert(ignore_permissions=True)
			self.db_set("tarefa", tarefa.name)
