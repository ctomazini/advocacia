frappe.ui.form.on('Fee Agreement', {
    refresh: function(frm) {
        controlar_campos(frm);
        controlar_grid_parcelas(frm);
        somar_totais(frm);

        if (!frm.is_new()) {
            frm.add_custom_button(__('Re-sincronizar Legal Payments'), function() {
                frappe.confirm(
                    __('Isso vai re-sincronizar todos os pagamentos com as parcelas atuais. Continuar?'),
                    function() {
                        frappe.call({
                            method: 'advocacia.advocacia.financeiro.resync_pagamentos_acordo',
                            args: { acordo_name: frm.doc.name },
                            freeze: true,
                            freeze_message: __('Sincronizando...'),
                            callback: function(r) {
                                if (r.message && r.message.status === 'ok') {
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            }).addClass('btn-primary-dark');
        }
    },
    fee_mode: function(frm) {
        controlar_campos(frm);
        controlar_grid_parcelas(frm);
        if (eh_direto(frm)) {
            // Limpa campos de divisão quando muda para Direto
            frm.set_value('lawyer_percentage', 0);
            frm.set_value('client_percentage', 0);
            frm.set_value('lawyer_amount', 0);
            frm.set_value('client_amount', 0);
            frm.set_value('fixed_fee_amount', 0);
            frm.set_value('contingency_fee_amount', 0);
            frm.set_value('contingency_fee_pct', 0);
        }
    },
    billing_type: function(frm) {
        controlar_campos(frm);
        calcular_valores(frm);
    },
    total_agreement_value: function(frm) {
        calcular_valores(frm);
    },
    lawyer_percentage: function(frm) {
        frm.set_value('client_percentage', 100 - (frm.doc.lawyer_percentage || 0));
        calcular_valores(frm);
    },
    fixed_fee_amount: function(frm) {
        calcular_valores(frm);
    },
    calculation_type: function(frm) {
        controlar_campos(frm);
        calcular_sucumbencia(frm);
    },
    contingency_fee_pct: function(frm) {
        calcular_sucumbencia(frm);
    },
    contingency_fee_amount: function(frm) {
        calcular_totais(frm);
    },
    installment_count: function(frm) {
        calcular_valores(frm);
    },
    generate_installments: function(frm) {
        gerar_tabela_parcelas(frm);
    }
});

frappe.ui.form.on('Fee Installment', {
    total_amount: function(frm, cdt, cdn) {
        if (!eh_direto(frm)) {
            return;
        }
        somar_totais(frm);
    },
    lawyer_amount: function(frm, cdt, cdn) {
        if (eh_direto(frm)) {
            return;
        }
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    client_amount: function(frm, cdt, cdn) {
        if (eh_direto(frm)) {
            return;
        }
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    contingency_amount: function(frm, cdt, cdn) {
        if (eh_direto(frm)) {
            return;
        }
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    parcelas_remove: function(frm) {
        somar_totais(frm);
    },
    parcelas_add: function(frm) {
        controlar_grid_parcelas(frm);
        somar_totais(frm);
    }
});

// === HELPERS ===

function eh_direto(frm) {
    return frm.doc.fee_mode === 'Honorários Diretos';
}

function recalcular_total_linha(cdt, cdn) {
    var row = locals[cdt][cdn];
    var total = (row.lawyer_amount || 0) + (row.client_amount || 0) + (row.contingency_amount || 0);
    frappe.model.set_value(cdt, cdn, 'total_amount', total);
}

function controlar_campos(frm) {
    var direto = eh_direto(frm);

    frm.set_df_property(
        'total_agreement_value',
        'label',
        __('Valor total contratado')
    );

    // --- Campos de divisão (ocultos no modo Direto) ---
    var campos_divisao = [
        'billing_type', 'lawyer_percentage', 'client_percentage',
        'fixed_fee_amount', 'lawyer_amount', 'client_amount'
    ];
    campos_divisao.forEach(function(f) {
        frm.set_df_property(f, 'hidden', direto ? 1 : 0);
    });

    // --- Seção Sucumbência (oculta no modo Direto) ---
    frm.set_df_property('contingency_section', 'hidden', direto ? 1 : 0);

    // --- Seção Totais: no modo Direto mostra só o total geral ---
    frm.set_df_property('lawyer_total', 'label', direto ? 'Total Honorários' : 'Total Advogada');
    frm.set_df_property('client_total', 'hidden', direto ? 1 : 0);

    // --- Lógica original dos sub-campos (só quando modo = Acordo com Divisão) ---
    if (!direto) {
        var tipo = frm.doc.billing_type;
        if (tipo === 'Valor fixo') {
            frm.set_df_property('lawyer_percentage', 'hidden', 1);
            frm.set_df_property('fixed_fee_amount', 'hidden', 0);
        } else if (tipo === 'Misto') {
            frm.set_df_property('lawyer_percentage', 'hidden', 0);
            frm.set_df_property('fixed_fee_amount', 'hidden', 0);
        } else {
            frm.set_df_property('lawyer_percentage', 'hidden', 0);
            frm.set_df_property('fixed_fee_amount', 'hidden', 1);
        }

        var tipo_suc = frm.doc.calculation_type;
        if (tipo_suc === 'Valor fixo') {
            frm.set_df_property('contingency_fee_pct', 'hidden', 1);
            frm.set_df_property('contingency_fee_amount', 'read_only', 0);
        } else {
            frm.set_df_property('contingency_fee_pct', 'hidden', 0);
            frm.set_df_property('contingency_fee_amount', 'read_only', 1);
        }
    }
}

function controlar_grid_parcelas(frm) {
    var grid = frm.fields_dict.fee_installments && frm.fields_dict.fee_installments.grid;
    if (!grid) {
        return;
    }
    var direto = eh_direto(frm);

    grid.update_docfield_property(
        'total_amount',
        'label',
        direto ? 'Valor do Contrato' : 'Valor Total'
    );
    grid.update_docfield_property('total_amount', 'read_only', direto ? 0 : 1);
    grid.update_docfield_property('lawyer_amount', 'hidden', direto ? 1 : 0);
    grid.update_docfield_property('client_amount', 'hidden', direto ? 1 : 0);
    grid.update_docfield_property('contingency_amount', 'hidden', direto ? 1 : 0);
    grid.update_docfield_property('payment', 'formatter', function(value) {
        if (!value) {
            return '';
        }
        return frappe.form.formatters.Link(value, {
            fieldtype: 'Link',
            options: 'Legal Payment',
            parent: 'Fee Installment'
        });
    });
    configurar_clique_pagamento_grid(frm);
    grid.refresh();
}

function configurar_clique_pagamento_grid(frm) {
    var grid = frm.fields_dict.fee_installments && frm.fields_dict.fee_installments.grid;
    if (!grid) {
        return;
    }

    if (!frm._pagamento_link_style) {
        frm._pagamento_link_style = true;
        frappe.dom.set_style(
            '.form-grid .grid-row [data-fieldname="payment"] .static-area, ' +
            '.form-grid .grid-row [data-fieldname="payment"] .link-field input[readonly] ' +
            '{ cursor: pointer; }'
        );
    }

    grid.wrapper.off('.advocacia-pagamento');

    grid.wrapper.on('mousedown.advocacia-pagamento', '[data-fieldname="payment"]', function(e) {
        if ($(e.target).closest('.btn-open, .btn-clear, .link-btn').length) {
            return;
        }

        var $row = $(this).closest('.grid-row');
        var idx = $row.attr('data-idx');
        if (!idx) {
            return;
        }

        var parcela = (frm.doc.fee_installments || []).find(function(r) {
            return String(r.idx) === String(idx);
        });
        if (!parcela || !parcela.payment) {
            return;
        }

        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        frappe.set_route('Form', 'Legal Payment', parcela.payment);
    });
}

function calcular_valores(frm) {
    var total = frm.doc.total_agreement_value || 0;

    if (eh_direto(frm)) {
        // Modo Direto: valor total = honorários integrais
        frm.set_value('lawyer_amount', 0);
        frm.set_value('client_amount', 0);
        var parcelas = frm.doc.installment_count || 0;
        if (parcelas > 0) {
            frm.set_value('installment_amount', total / parcelas);
        }
        frm.set_value('lawyer_total', total);
        frm.set_value('client_total', 0);
        return;
    }

    // Modo Acordo com Divisão (lógica original)
    var tipo = frm.doc.billing_type;
    if (tipo === 'Valor fixo') {
        var fixo = frm.doc.fixed_fee_amount || 0;
        frm.set_value('lawyer_amount', fixo);
        frm.set_value('client_amount', total - fixo);
        if (total > 0) {
            frm.set_value('lawyer_percentage', (fixo / total) * 100);
            frm.set_value('client_percentage', 100 - ((fixo / total) * 100));
        }
    } else if (tipo === 'Misto') {
        var perc_adv = frm.doc.lawyer_percentage || 0;
        var fixo = frm.doc.fixed_fee_amount || 0;
        var valor_perc = total * perc_adv / 100;
        frm.set_value('lawyer_amount', valor_perc + fixo);
        frm.set_value('client_amount', total - valor_perc - fixo);
        if (total > 0) {
            frm.set_value('client_percentage', 100 - perc_adv - ((fixo / total) * 100));
        }
    } else {
        var perc_adv = frm.doc.lawyer_percentage || 0;
        frm.set_value('client_percentage', 100 - perc_adv);
        frm.set_value('lawyer_amount', total * perc_adv / 100);
        frm.set_value('client_amount', total * (100 - perc_adv) / 100);
    }
    var parcelas = frm.doc.installment_count || 0;
    if (parcelas > 0) {
        frm.set_value('installment_amount', (frm.doc.lawyer_amount || 0) / parcelas);
    }
    calcular_sucumbencia(frm);
}

function calcular_sucumbencia(frm) {
    if (eh_direto(frm)) return;
    var total = frm.doc.total_agreement_value || 0;
    var tipo_suc = frm.doc.calculation_type;
    if (tipo_suc !== 'Valor fixo') {
        var perc_suc = frm.doc.contingency_fee_pct || 0;
        frm.set_value('contingency_fee_amount', total * perc_suc / 100);
    }
    calcular_totais(frm);
}

function calcular_totais(frm) {
    if (eh_direto(frm)) {
        frm.set_value('lawyer_total', frm.doc.total_agreement_value || 0);
        frm.set_value('client_total', 0);
        return;
    }
    var valor_adv = frm.doc.lawyer_amount || 0;
    var sucumbencia = frm.doc.contingency_fee_amount || 0;
    var valor_cli = frm.doc.client_amount || 0;
    frm.set_value('lawyer_total', valor_adv + sucumbencia);
    frm.set_value('client_total', valor_cli);
}

function gerar_tabela_parcelas(frm) {
    var parcelas = frm.doc.installment_count || 0;
    var data_inicio = frm.doc.first_installment_date;
    var total = frm.doc.total_agreement_value || 0;
    var direto = eh_direto(frm);

    if (!parcelas || parcelas <= 0) {
        frappe.msgprint('Preencha o número de parcelas.');
        return;
    }
    if (!data_inicio) {
        frappe.msgprint('Preencha a data da primeira parcela.');
        return;
    }
    if (!total) {
        frappe.msgprint(__('Preencha o valor total contratado.'));
        return;
    }

    if (direto) {
        // Modo Direto: parcelas simples, sem divisão nem sucumbência
        var valor_parcela = total / parcelas;
        frm.clear_table('fee_installments');
        for (var i = 0; i < parcelas; i++) {
            var dt = frappe.datetime.add_months(data_inicio, i);
            var row = frm.add_child('fee_installments');
            row.due_date = dt;
            row.lawyer_amount = 0;
            row.client_amount = 0;
            row.contingency_amount = 0;
            row.total_amount = valor_parcela;
            row.description = 'Parcela ' + (i + 1) + ' de ' + parcelas;
            row.status = 'Pendente';
        }
        frm.refresh_field('fee_installments');
        somar_totais(frm);
        frappe.msgprint(parcelas + ' parcelas geradas com sucesso!');
        return;
    }

    // Modo Acordo com Divisão (lógica original com prompt de sucumbência)
    var valor_adv = frm.doc.lawyer_amount || 0;
    var valor_cli = frm.doc.client_amount || 0;
    var sucumbencia = frm.doc.contingency_fee_amount || 0;

    frappe.prompt([
        {
            fieldname: 'incluir_sucumbencia',
            label: 'Incluir sucumbência nas parcelas?',
            fieldtype: 'Select',
            options: 'Não incluir\nNa primeira parcela\nNa última parcela\nDividir igualmente',
            default: 'Não incluir',
            reqd: 1
        }
    ], function(values) {
        var parcela_adv = valor_adv / parcelas;
        var parcela_cli = valor_cli / parcelas;
        frm.clear_table('fee_installments');
        for (var i = 0; i < parcelas; i++) {
            var dt = frappe.datetime.add_months(data_inicio, i);
            var row = frm.add_child('fee_installments');
            row.due_date = dt;
            row.lawyer_amount = parcela_adv;
            row.client_amount = parcela_cli;
            row.contingency_amount = 0;
            row.description = 'Parcela ' + (i + 1) + ' de ' + parcelas;
            row.status = 'Pendente';
            if (values.incluir_sucumbencia === 'Na primeira parcela' && i === 0) {
                row.contingency_amount = sucumbencia;
                row.description += ' + Sucumbência';
            } else if (values.incluir_sucumbencia === 'Na última parcela' && i === parcelas - 1) {
                row.contingency_amount = sucumbencia;
                row.description += ' + Sucumbência';
            } else if (values.incluir_sucumbencia === 'Dividir igualmente') {
                row.contingency_amount = sucumbencia / parcelas;
            }
            row.total_amount = row.lawyer_amount + row.client_amount + row.contingency_amount;
        }
        frm.refresh_field('fee_installments');
        somar_totais(frm);
        frappe.msgprint(parcelas + ' parcelas geradas com sucesso!');
    }, 'Como distribuir a sucumbência?', 'Gerar');
}

function somar_totais(frm) {
    if (eh_direto(frm)) {
        var total_parcelas = 0;
        (frm.doc.fee_installments || []).forEach(function(row) {
            total_parcelas += row.total_amount || 0;
        });
        frm.set_value('lawyer_total', total_parcelas || frm.doc.total_agreement_value || 0);
        frm.set_value('client_total', 0);
        return;
    }
    var total_adv = 0;
    var total_cli = 0;
    var total_suc = 0;
    (frm.doc.fee_installments || []).forEach(function(row) {
        total_adv += row.lawyer_amount || 0;
        total_cli += row.client_amount || 0;
        total_suc += row.contingency_amount || 0;
    });
    frm.set_value('lawyer_total', total_adv + total_suc);
    frm.set_value('client_total', total_cli);
}
