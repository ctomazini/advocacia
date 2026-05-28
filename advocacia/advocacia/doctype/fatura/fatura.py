import frappe
from frappe.model.document import Document
from frappe.utils import today


class Fatura(Document):
    def before_save(self):
        self.atualizar_status()

    def atualizar_status(self):
        if self.status == "Cancelada":
            return
        if self.data_pagamento:
            self.status = "Paga"
        elif self.data_vencimento and str(self.data_vencimento) < today():
            self.status = "Vencida"
        else:
            self.status = "Pendente"

    @frappe.whitelist()
    def registrar_pagamento(self):
        self.data_pagamento = today()
        self.status = "Paga"
        self.save()
        return {"status": "Paga", "data_pagamento": self.data_pagamento}
