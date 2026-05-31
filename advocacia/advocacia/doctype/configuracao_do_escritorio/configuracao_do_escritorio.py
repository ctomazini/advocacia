import frappe
from frappe.model.document import Document

from advocacia.advocacia.validators import validar_cnpj


class ConfiguracaodoEscritorio(Document):
	def validate(self):
		if self.cnpj:
			self.cnpj = validar_cnpj(self.cnpj)
