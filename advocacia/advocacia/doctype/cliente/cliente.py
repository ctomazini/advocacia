import frappe
from frappe.model.document import Document

from advocacia.advocacia.validators import (
    limpar_numerico,
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
            self.cnpj = None
        else:
            self.cpf = None
            self.rg = None
            self.estado_civil = None
            self.profissao = None
            self.nacionalidade = self.nacionalidade or "Brasileira"

    def validate(self):
        if self.tipo_pessoa == "Pessoa Física":
            if self.cpf:
                self.cpf = validar_cpf(self.cpf)
            if self.cpf_representante:
                self.cpf_representante = validar_cpf(self.cpf_representante)
        elif self.tipo_pessoa == "Pessoa Jurídica":
            if self.cnpj:
                self.cnpj = validar_cnpj(self.cnpj)

        if getattr(self, "email", None):
            self.email = validar_email(self.email)

        for contato in self.contatos or []:
            if contato.telefone:
                contato.telefone = validar_telefone(contato.telefone, tipo="fixo")
            if contato.celular:
                contato.celular = validar_telefone(contato.celular, tipo="celular")
            if contato.email:
                contato.email = validar_email(contato.email)
