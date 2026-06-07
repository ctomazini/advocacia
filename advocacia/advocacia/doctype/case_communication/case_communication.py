import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class CaseCommunication(Document):
	def validate(self):
		if not self.tipo:
			frappe.throw(_("Tipo é obrigatório."))
		if self.legal_case and not self.client:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)
		self._criar_tarefa_vinculada()

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def on_update(self):
		self._criar_tarefa_vinculada()

	def _criar_tarefa_vinculada(self):
		"""Cria Legal Task de follow-up uma única vez, se solicitado."""
		if not self.gerar_tarefa or not self.proximos_passos or self.legal_task:
			return

		tarefa = frappe.get_doc(
			{
				"doctype": "Legal Task",
				"titulo": f"Follow-up: {self.assunto}",
				"descricao": self.proximos_passos,
				"legal_case": self.legal_case,
				"client": self.client,
				"status": "Pendente",
				"data_limite": add_days(today(), 3),
			}
		)
		frappe.has_permission("Legal Task", "create", throw=True)
		tarefa.insert()
		self.db_set("legal_task", tarefa.name)
