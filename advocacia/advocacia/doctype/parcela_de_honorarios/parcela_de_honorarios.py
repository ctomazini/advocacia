import frappe
from frappe.model.document import Document
from frappe.utils import today


class ParcelaDeHonorarios(Document):
    def before_save(self):
        self.atualizar_status()

    def atualizar_status(self):
        if self.status in ("Cancelada", "Repassada"):
            return
        if self.data_recebimento:
            if self.valor_cliente and self.valor_cliente > 0:
                if self.data_repasse:
                    self.status = "Repassada"
                else:
                    self.status = "Recebida"
            else:
                self.status = "Recebida"
        elif self.vencimento and str(self.vencimento) < today():
            self.status = "Vencida"
        else:
            self.status = "Pendente"

    @frappe.whitelist()
    def registrar_recebimento(self):
        self.data_recebimento = today()
        self.atualizar_status()
        self.save()
        return {"status": self.status}

    @frappe.whitelist()
    def registrar_repasse(self):
        self.data_repasse = today()
        self.status = "Repassada"
        self.save()
        return {"status": self.status}
