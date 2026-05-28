import frappe
from frappe.model.document import Document
from frappe.utils import today


class Tarefa(Document):
    def before_save(self):
        if self.status == "Concluída" and not self.data_conclusao:
            self.data_conclusao = today()

    @frappe.whitelist()
    def concluir(self):
        self.status = "Concluída"
        self.data_conclusao = today()
        self.save()
        return {"status": self.status}
