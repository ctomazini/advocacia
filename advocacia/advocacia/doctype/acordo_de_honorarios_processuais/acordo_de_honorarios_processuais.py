import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class AcordodeHonorariosProcessuais(Document):
    def validate(self):
        if not self.cliente and self.servico:
            self.cliente = frappe.db.get_value("Servico", self.servico, "cliente")
        if not self.cliente:
            frappe.throw(_("Cliente é obrigatório. Selecione um Serviço válido."))
        self._validar_financeiro()
        self._validar_parcelas()

    def _eh_direto(self):
        return self.modo_honorarios == "Honorários Diretos"

    def _validar_financeiro(self):
        total_acordo = flt(self.valor_total_do_acordo)
        parcelas = self.get("table_ztjx") or []

        if parcelas and total_acordo <= 0:
            frappe.throw(_("Valor total do acordo deve ser maior que zero."))

        if self.get("número_de_parcelas") and flt(self.número_de_parcelas) > 0:
            if not self.data_primeira_parcela:
                frappe.throw(_("Informe a data da primeira parcela."))
            if total_acordo <= 0:
                frappe.throw(_("Valor total do acordo deve ser maior que zero para gerar parcelas."))

        if self._eh_direto():
            return

        tipo_cobranca = self.get("tipo_de_cobrança")
        if tipo_cobranca in ("Percentual do acordo", "Percentual da causa"):
            perc_adv = flt(self.percentual_advogada)
            perc_cli = flt(self.percentual_cliente)
            if abs(perc_adv + perc_cli - 100) > 0.02:
                frappe.throw(
                    _("Percentual advogada ({0}%) + cliente ({1}%) deve somar 100%.").format(
                        perc_adv, perc_cli
                    )
                )

        if tipo_cobranca == "Misto":
            perc_adv = flt(self.percentual_advogada)
            if perc_adv < 0 or perc_adv > 100:
                frappe.throw(_("Percentual da advogada deve estar entre 0 e 100."))
            if flt(self.valor_fixo_de_honorarios) < 0:
                frappe.throw(_("Valor fixo de honorários não pode ser negativo."))

        if total_acordo > 0 and not self._eh_direto():
            valor_adv = flt(self.valor_advogada)
            valor_cli = flt(self.valor_cliente)
            sucumbencia = flt(self.get("honorários_de_sucumbência"))
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

        tipo_suc = self.get("tipo_de_cálculo")
        if tipo_suc == "Percentual" and total_acordo > 0:
            perc_suc = flt(self.get("percentual_sucumbência"))
            if perc_suc < 0 or perc_suc > 100:
                frappe.throw(_("Percentual de sucumbência deve estar entre 0 e 100."))

    def _validar_parcelas(self):
        parcelas = self.get("table_ztjx") or []
        if not parcelas:
            return

        erros = []
        data_primeira = getdate(self.data_primeira_parcela) if self.data_primeira_parcela else None

        if self._eh_direto():
            total_parcelas = sum(flt(p.valor_total) for p in parcelas)
            total_acordo = flt(self.valor_total_do_acordo)
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
            valor_adv_esperado = flt(self.valor_advogada)
            valor_cli_esperado = flt(self.valor_cliente)
            suc_esperada = flt(self.get("honorários_de_sucumbência"))
            total_esperado = valor_adv_esperado + valor_cli_esperado + suc_esperada

            for p in parcelas:
                soma_linha = (
                    flt(p.valor_advogada) + flt(p.valor_cliente) + flt(p.get("valor_sucumbência"))
                )
                if abs(soma_linha - flt(p.valor_total)) > 0.02:
                    erros.append(
                        _("Parcela {0}: soma dos valores ≠ valor total da linha.").format(p.idx)
                    )
                if flt(p.valor_cliente) < 0:
                    erros.append(_("Parcela {0}: valor do cliente negativo.").format(p.idx))
                if data_primeira and p.vencimento and getdate(p.vencimento) < data_primeira:
                    erros.append(
                        _("Parcela {0}: vencimento anterior à data da primeira parcela.").format(p.idx)
                    )
                total_adv_tabela += flt(p.valor_advogada)
                total_cli_tabela += flt(p.valor_cliente)
                total_suc_tabela += flt(p.get("valor_sucumbência"))
                total_geral_tabela += flt(p.valor_total)

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
