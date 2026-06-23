import frappe
from frappe.model.document import Document

from advocacia.advocacia.validators import validar_cnpj, validar_cpf


class OfficeSettings(Document):
	def validate(self):
		if self.cnpj:
			self.cnpj = validar_cnpj(self.cnpj)
		if self.lawyer_cpf:
			self.lawyer_cpf = validar_cpf(self.lawyer_cpf)
