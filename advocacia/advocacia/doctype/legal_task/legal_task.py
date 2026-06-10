import frappe
from frappe.model.document import Document
from frappe.utils import today

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class LegalTask(Document):
	def validate(self):
		if self.legal_case and not self.client:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def before_save(self):
		if self.status == "Concluída" and not self.completion_date:
			self.completion_date = today()

	@frappe.whitelist()
	def concluir(self) -> dict:
		frappe.has_permission("Legal Task", "write", doc=self, throw=True)
		self.status = "Concluída"
		self.completion_date = today()
		self.save()
		return {"status": self.status}
