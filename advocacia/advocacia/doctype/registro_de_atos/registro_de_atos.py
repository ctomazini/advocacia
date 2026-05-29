import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RegistrodeAtos(Document):
    def validate(self):
        self._calcular_totais()
        self._atualizar_status()

    def _calcular_totais(self):
        pendente = 0
        cobrado = 0
        for row in self.atos or []:
            valor = flt(row.valor)
            if row.status == "Pendente":
                pendente += valor
            elif row.status == "Cobrado":
                cobrado += valor
        self.total_pendente = pendente
        self.total_cobrado = cobrado
        self.total_geral = pendente + cobrado

    def _atualizar_status(self):
        if not self.atos:
            self.status = "Em aberto"
            return
        tem_pendente = any(row.status == "Pendente" for row in self.atos)
        tem_cobrado = any(row.status == "Cobrado" for row in self.atos)
        if tem_pendente and tem_cobrado:
            self.status = "Parcialmente cobrado"
        elif not tem_pendente and tem_cobrado:
            self.status = "Cobrado"
        else:
            self.status = "Em aberto"
