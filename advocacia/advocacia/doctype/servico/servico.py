import frappe
from frappe.model.document import Document

from advocacia.advocacia.validators import limpar_numerico, validar_cnj


class Servico(Document):
    def validate(self):
        if self.numero_processo:
            self.numero_processo = validar_cnj(self.numero_processo)
            self.numero_processo = limpar_numerico(self.numero_processo)
