import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class RegistrodeAtos(Document):
	def validate(self):
		if not self.cliente and self.servico:
			self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
		if not self.cliente:
			frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))
		recompor_titulo_se_vazio(self)
		self._validar_reversao_atos_faturados()
		self._calcular_totais()
		self._atualizar_status()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _validar_reversao_atos_faturados(self):
		if getattr(frappe.flags, "in_atos_cobranca_sync", False):
			return

		old_rows = {}
		if not self.is_new() and self.name:
			old_doc = frappe.get_doc("Registro de Atos", self.name)
			old_rows = {row.name: row for row in old_doc.atos or [] if row.name}

		for ato in self.atos or []:
			if ato.status != "Pendente":
				continue

			cobranca_id = ato.cobranca_id
			if not cobranca_id and ato.name:
				prev = old_rows.get(ato.name)
				if prev and prev.status == "Cobrado":
					cobranca_id = prev.cobranca_id

			if not cobranca_id:
				continue

			if not frappe.db.exists("Pagamento", cobranca_id):
				continue

			pay_status = frappe.db.get_value("Pagamento", cobranca_id, "status")
			if pay_status and pay_status != "Cancelado":
				frappe.throw(
					_(
						"Não é permitido voltar o ato para Pendente enquanto o pagamento {0} estiver ativo. "
						"Cancele o pagamento primeiro."
					).format(cobranca_id),
					title=_("Ato já faturado"),
				)

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
