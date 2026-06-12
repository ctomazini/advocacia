import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from advocacia.advocacia.titulos import aplicar_titulo_pos_insert, recompor_titulo_se_vazio


class FeeAgreement(Document):
	def validate(self):
		if not self.client and self.legal_case:
			self.client = frappe.db.get_value("Legal Case", self.legal_case, "client")
		if not self.client:
			frappe.throw(_("Client é obrigatório. Selecione um Serviço válido."))
		self._validar_financeiro()
		self._validar_parcelas()
		self._compor_titulo()

	def after_insert(self):
		aplicar_titulo_pos_insert(self)

	def _compor_titulo(self):
		recompor_titulo_se_vazio(self)

	def _eh_direto(self):
		return self.fee_mode == "Honorários Diretos"

	def _validar_financeiro(self):
		total_acordo = flt(self.total_agreement_value)
		parcelas = self.get("fee_installments") or []

		if parcelas and total_acordo <= 0:
			frappe.throw(_("Valor total do acordo deve ser maior que zero."))

		if self.get("installment_count") and flt(self.installment_count) > 0:
			parcelas_cfg = self.get("fee_installments") or []
			has_fixed_date = any(
				(row.payment_condition or "Data fixa") == "Data fixa" for row in parcelas_cfg
			)
			if has_fixed_date and not self.first_installment_date:
				frappe.throw(_("Informe a data da primeira parcela."))
			if total_acordo <= 0:
				frappe.throw(_("Valor total do acordo deve ser maior que zero para gerar parcelas."))

		if self._eh_direto():
			return

		tipo_cobranca = self.get("billing_type")
		if tipo_cobranca in ("Percentual do acordo", "Percentual da causa"):
			perc_adv = flt(self.lawyer_percentage)
			perc_cli = flt(self.client_percentage)
			if abs(perc_adv + perc_cli - 100) > 0.02:
				frappe.throw(
					_("Percentual advogada ({0}%) + cliente ({1}%) deve somar 100%.").format(
						perc_adv, perc_cli
					)
				)

		if tipo_cobranca == "Misto":
			perc_adv = flt(self.lawyer_percentage)
			if perc_adv < 0 or perc_adv > 100:
				frappe.throw(_("Percentual da advogada deve estar entre 0 e 100."))
			if flt(self.fixed_fee_amount) < 0:
				frappe.throw(_("Valor fixo de honorários não pode ser negativo."))

		if total_acordo > 0 and not self._eh_direto():
			valor_adv = flt(self.lawyer_amount)
			valor_cli = flt(self.client_amount)
			sucumbencia = flt(self.get("contingency_fee_amount"))
			if valor_cli < 0:
				frappe.throw(_("Valor do cliente não pode ser negativo."))
			if sucumbencia < 0:
				frappe.throw(_("Honorários de sucumbência não podem ser negativos."))
			soma_base = valor_adv + valor_cli
			if abs(soma_base - total_acordo) > 0.05:
				frappe.throw(
					_("Soma advogada + cliente (R$ {0}) difere do valor total do acordo (R$ {1}).").format(
						soma_base, total_acordo
					)
				)

		tipo_suc = self.get("calculation_type")
		if tipo_suc == "Percentual" and total_acordo > 0:
			perc_suc = flt(self.get("contingency_fee_pct"))
			if perc_suc < 0 or perc_suc > 100:
				frappe.throw(_("Percentual de sucumbência deve estar entre 0 e 100."))

	def _validar_parcelas(self):
		parcelas = self.get("fee_installments") or []
		if not parcelas:
			return

		erros = []
		data_primeira = getdate(self.first_installment_date) if self.first_installment_date else None

		for p in parcelas:
			condition = p.payment_condition or "Data fixa"
			if condition == "Data fixa" and not p.due_date:
				erros.append(
					_("Parcela {0}: informe vencimento para condição Data fixa.").format(p.idx)
				)
			if data_primeira and p.due_date and getdate(p.due_date) < data_primeira:
				erros.append(
					_("Parcela {0}: vencimento anterior à data da primeira parcela.").format(p.idx)
				)

		if self._eh_direto():
			total_parcelas = sum(flt(p.total_amount) for p in parcelas)
			total_acordo = flt(self.total_agreement_value)
			if abs(total_parcelas - total_acordo) > 0.02:
				erros.append(
					_("Soma das parcelas (R$ {0}) ≠ valor total do acordo (R$ {1}).").format(
						total_parcelas, total_acordo
					)
				)
		else:
			total_adv_tabela = 0
			total_cli_tabela = 0
			total_suc_tabela = 0
			total_geral_tabela = 0
			valor_adv_esperado = flt(self.lawyer_amount)
			valor_cli_esperado = flt(self.client_amount)
			suc_esperada = flt(self.get("contingency_fee_amount"))
			total_esperado = valor_adv_esperado + valor_cli_esperado + suc_esperada

			for p in parcelas:
				soma_linha = (
					flt(p.lawyer_amount) + flt(p.client_amount) + flt(p.get("contingency_amount"))
				)
				if abs(soma_linha - flt(p.total_amount)) > 0.02:
					erros.append(
						_("Parcela {0}: soma dos valores ≠ valor total da linha.").format(p.idx)
					)
				if flt(p.client_amount) < 0:
					erros.append(_("Parcela {0}: valor do cliente negativo.").format(p.idx))
				total_adv_tabela += flt(p.lawyer_amount)
				total_cli_tabela += flt(p.client_amount)
				total_suc_tabela += flt(p.get("contingency_amount"))
				total_geral_tabela += flt(p.total_amount)

			if abs(total_adv_tabela - valor_adv_esperado) > 0.02:
				erros.append(_("Soma advogada nas parcelas ≠ valor advogada do formulário."))
			if abs(total_cli_tabela - valor_cli_esperado) > 0.02:
				erros.append(_("Soma cliente nas parcelas ≠ valor cliente do formulário."))
			if abs(total_suc_tabela - suc_esperada) > 0.02:
				erros.append(_("Soma sucumbência nas parcelas ≠ sucumbência do formulário."))
			if abs(total_geral_tabela - total_esperado) > 0.02:
				erros.append(_("Soma total das parcelas ≠ total esperado do acordo."))

		if erros:
			frappe.throw(
				"<br>".join(erros),
				title=_("Erro de validação das parcelas"),
			)
