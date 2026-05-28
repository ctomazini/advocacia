import frappe
from frappe.model.document import Document


class Cliente(Document):
    def before_save(self):
        # Limpa campos que não pertencem ao tipo de pessoa
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
