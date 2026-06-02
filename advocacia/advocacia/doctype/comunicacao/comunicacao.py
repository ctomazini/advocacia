import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class Comunicacao(Document):
	def validate(self):
		if not self.tipo:
			frappe.throw(_("Tipo é obrigatório."))
		if self.servico and not self.cliente:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)
		self._criar_tarefa_vinculada()

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def on_update(self):
		self._criar_tarefa_vinculada()

	def _criar_tarefa_vinculada(self):
		"""Cria Tarefa de follow-up uma única vez, se solicitado."""
		if not self.gerar_tarefa or not self.proximos_passos or self.tarefa:
			return

		tarefa = frappe.get_doc(
			{
				"doctype": "Tarefa",
				"titulo": f"Follow-up: {self.assunto}",
				"descricao": self.proximos_passos,
				"servico": self.servico,
				"cliente": self.cliente,
				"status": "Pendente",
				"data_limite": add_days(today(), 3),
			}
		)
		tarefa.insert(ignore_permissions=True)
		self.db_set("tarefa", tarefa.name)
