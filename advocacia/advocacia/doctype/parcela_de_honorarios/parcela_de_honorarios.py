import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class ParceladeHonorarios(Document):
	def before_insert(self):
		if not self.parcela_origem_id:
			self.parcela_origem_id = "PARC-{0}".format(frappe.generate_hash(length=12))

	def validate(self):
		if not self.is_new() and self.name:
			old_id = frappe.db.get_value(self.doctype, self.name, "parcela_origem_id")
			if old_id and self.parcela_origem_id and self.parcela_origem_id != old_id:
				frappe.throw(_("ID de origem da parcela não pode ser alterado."))

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
