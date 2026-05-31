import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds


class RegistrodeHoras(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")

		if self.hora_inicio and self.hora_fim and not self.duracao_minutos:
			diff = time_diff_in_seconds(self.hora_fim, self.hora_inicio)
			self.duracao_minutos = max(0, int(diff / 60))

		if self.duracao_minutos:
			self.duracao_horas = round(self.duracao_minutos / 60, 2)
