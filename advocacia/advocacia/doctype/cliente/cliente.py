import frappe
from frappe import _
from frappe.model.document import Document

from advocacia.advocacia.validators import (
	validar_cnpj,
	validar_cpf,
	validar_email,
	validar_telefone,
)


class Cliente(Document):
	def before_save(self):
		if self.tipo_pessoa == "Pessoa Física":
			self.nome_fantasia = None
			self.representante = None
			self.cargo_representante = None
			self.cpf_representante = None
			self.nacionalidade_pj = None
			self.cnpj = None
		else:
			self.cpf = None
			self.rg = None
			self.estado_civil = None
			self.profissao = None
			self.nacionalidade = None

	def validate(self):
		if self.tipo_pessoa == "Pessoa Física":
			if not self.cpf:
				frappe.throw(
					_("CPF é obrigatório para Pessoa Física."),
					title=_("Campo obrigatório"),
				)
			self.cpf = validar_cpf(self.cpf)
		elif self.tipo_pessoa == "Pessoa Jurídica":
			if not self.cnpj:
				frappe.throw(
					_("CNPJ é obrigatório para Pessoa Jurídica."),
					title=_("Campo obrigatório"),
				)
			self.cnpj = validar_cnpj(self.cnpj)
			if self.cpf_representante:
				self.cpf_representante = validar_cpf(self.cpf_representante)

		self._validar_unicidade_documento()

		for contato in self.contatos or []:
			if contato.telefone:
				contato.telefone = validar_telefone(contato.telefone, tipo="fixo")
			if contato.celular:
				contato.celular = validar_telefone(contato.celular, tipo="celular")
			if contato.email:
				contato.email = validar_email(contato.email)

	def _validar_unicidade_documento(self):
		if self.tipo_pessoa == "Pessoa Física" and self.cpf:
			duplicado = frappe.db.exists(
				"Cliente",
				{"cpf": self.cpf, "name": ["!=", self.name]},
			)
			if duplicado:
				frappe.throw(
					_("Já existe cliente cadastrado com o CPF {0}.").format(self.cpf),
					title=_("CPF duplicado"),
				)
		elif self.tipo_pessoa == "Pessoa Jurídica" and self.cnpj:
			duplicado = frappe.db.exists(
				"Cliente",
				{"cnpj": self.cnpj, "name": ["!=", self.name]},
			)
			if duplicado:
				frappe.throw(
					_("Já existe cliente cadastrado com o CNPJ {0}.").format(self.cnpj),
					title=_("CNPJ duplicado"),
				)
