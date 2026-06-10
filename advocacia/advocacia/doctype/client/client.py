import frappe
from frappe import _
from frappe.model.document import Document

from advocacia.advocacia.validators import (
	validar_cnpj,
	validar_cpf,
	validar_email,
	validar_telefone,
)


class Client(Document):
	def before_save(self):
		if self.person_type == "Pessoa Física":
			self.trade_name = None
			self.representative = None
			self.representative_role = None
			self.representative_cpf = None
			self.representative_nationality = None
			self.cnpj = None
		else:
			self.cpf = None
			self.rg = None
			self.marital_status = None
			self.occupation = None
			self.nationality = None

	def validate(self):
		if self.person_type == "Pessoa Física":
			if not self.cpf:
				frappe.throw(
					_("CPF é obrigatório para Pessoa Física."),
					title=_("Campo obrigatório"),
				)
			self.cpf = validar_cpf(self.cpf)
		elif self.person_type == "Pessoa Jurídica":
			if not self.cnpj:
				frappe.throw(
					_("CNPJ é obrigatório para Pessoa Jurídica."),
					title=_("Campo obrigatório"),
				)
			self.cnpj = validar_cnpj(self.cnpj)
			if self.representative_cpf:
				self.representative_cpf = validar_cpf(self.representative_cpf)

		self._validar_unicidade_documento()

		for contato in self.contacts or []:
			if contato.phone:
				contato.phone = validar_telefone(contato.phone, phone_type="landline")
			if contato.mobile:
				contato.mobile = validar_telefone(contato.mobile, phone_type="mobile")
			if contato.email:
				contato.email = validar_email(contato.email)

	def _validar_unicidade_documento(self):
		if self.person_type == "Pessoa Física" and self.cpf:
			duplicado = frappe.db.exists(
				"Client",
				{"cpf": self.cpf, "name": ["!=", self.name]},
			)
			if duplicado:
				frappe.throw(
					_("Já existe cliente cadastrado com o CPF {0}.").format(self.cpf),
					title=_("CPF duplicado"),
				)
		elif self.person_type == "Pessoa Jurídica" and self.cnpj:
			duplicado = frappe.db.exists(
				"Client",
				{"cnpj": self.cnpj, "name": ["!=", self.name]},
			)
			if duplicado:
				frappe.throw(
					_("Já existe cliente cadastrado com o CNPJ {0}.").format(self.cnpj),
					title=_("CNPJ duplicado"),
				)
