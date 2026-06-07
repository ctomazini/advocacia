import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class ServiceRecord(Document):
	def validate(self):
		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		if not self.client:
			frappe.throw(_("Client é obrigatório. Selecione um Serviço válido."))
		self._compor_titulo()
		self._validar_reversao_atos_faturados()
		self._calcular_totais()
		self._atualizar_status()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def _validar_reversao_atos_faturados(self):
		if getattr(frappe.flags, "in_atos_cobranca_sync", False):
			return

		old_rows = {}
		if not self.is_new() and self.name:
			old_doc = frappe.get_doc("Service Record", self.name)
			old_rows = {row.name: row for row in old_doc.acts or [] if row.name}

		pagamento_refs = set()
		pending_checks = []

		for ato in self.acts or []:
			if ato.status != "Pendente":
				continue

			pagamento_name = ato.payment
			if not pagamento_name and ato.name:
				prev = old_rows.get(ato.name)
				if prev and prev.status == "Cobrado":
					pagamento_name = prev.payment

			if not pagamento_name:
				continue

			pagamento_refs.add(pagamento_name)
			pending_checks.append(pagamento_name)

		if not pagamento_refs:
			return

		status_by_name = {
			row.name: row.status
			for row in frappe.get_all(
				"Legal Payment",
				filters={"name": ["in", list(pagamento_refs)]},
				fields=["name", "status"],
			)
		}

		for pagamento_name in pending_checks:
			pay_status = status_by_name.get(pagamento_name)
			if not pay_status or pay_status == "Cancelado":
				continue
			frappe.throw(
				_(
					"Não é permitido voltar o ato para Pendente enquanto o pagamento {0} estiver ativo. "
					"Cancele o pagamento primeiro."
				).format(pagamento_name),
				title=_("Ato já faturado"),
			)

	def _calcular_totais(self):
		pendente = 0
		cobrado = 0
		for row in self.acts or []:
			valor = flt(row.valor)
			if row.status == "Pendente":
				pendente += valor
			elif row.status == "Cobrado":
				cobrado += valor
		self.total_pendente = pendente
		self.total_cobrado = cobrado
		self.total_geral = pendente + cobrado

	def _atualizar_status(self):
		if not self.acts:
			self.status = "Em aberto"
			return
		tem_pendente = any(row.status == "Pendente" for row in self.acts)
		tem_cobrado = any(row.status == "Cobrado" for row in self.acts)
		if tem_pendente and tem_cobrado:
			self.status = "Parcialmente cobrado"
		elif not tem_pendente and tem_cobrado:
			self.status = "Cobrado"
		else:
			self.status = "Em aberto"
