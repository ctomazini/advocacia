import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class FeeInstallment(Document):
	def before_insert(self):
		if not self.installment_origin_id:
			self.installment_origin_id = "PARC-{0}".format(frappe.generate_hash(length=12))

	def validate(self):
		if not self.is_new() and self.name:
			old_id = frappe.db.get_value(self.doctype, self.name, "installment_origin_id")
			if old_id and self.installment_origin_id and self.installment_origin_id != old_id:
				frappe.throw(_("ID de origem da parcela n?o pode ser alterado."))

	def before_save(self):
		self.atualizar_status()

	def atualizar_status(self):
		if self.status in ("Cancelado", "Repassado"):
			return
		if self.received_date:
			if self.client_amount and self.client_amount > 0:
				if self.transfer_date:
					self.status = "Repassado"
				else:
					self.status = "Recebido"
			else:
				self.status = "Recebido"
		elif self.due_date and str(self.due_date) < today():
			self.status = "Vencido"
		else:
			self.status = "Pendente"

	@frappe.whitelist()
	def registrar_recebimento(self) -> dict:
		frappe.has_permission("Fee Agreement", "write", throw=True)
		self.received_date = today()
		self.atualizar_status()
		self.save()
		return {"status": self.status}

	@frappe.whitelist()
	def registrar_repasse(self) -> dict:
		frappe.has_permission("Fee Agreement", "write", throw=True)
		self.transfer_date = today()
		self.status = "Repassado"
		self.save()
		return {"status": self.status}
