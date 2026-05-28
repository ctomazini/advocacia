frappe.ui.form.on('Acordo de Honorarios Processuais', {
    refresh: function(frm) {
        controlar_campos(frm);
        somar_totais(frm);
    },
    modo_honorarios: function(frm) {
        controlar_campos(frm);
        if (eh_direto(frm)) {
            // Limpa campos de divisão quando muda para Direto
            frm.set_value('percentual_advogada', 0);
            frm.set_value('percentual_cliente', 0);
            frm.set_value('valor_advogada', 0);
            frm.set_value('valor_cliente', 0);
            frm.set_value('valor_fixo_de_honorarios', 0);
            frm.set_value('honorários_de_sucumbência', 0);
            frm.set_value('percentual_sucumbência', 0);
        }
    },
    tipo_de_cobrança: function(frm) {
        controlar_campos(frm);
        calcular_valores(frm);
    },
    valor_total_do_acordo: function(frm) {
        calcular_valores(frm);
    },
    percentual_advogada: function(frm) {
        frm.set_value('percentual_cliente', 100 - (frm.doc.percentual_advogada || 0));
        calcular_valores(frm);
    },
    valor_fixo_de_honorarios: function(frm) {
        calcular_valores(frm);
    },
    tipo_de_cálculo: function(frm) {
        controlar_campos(frm);
        calcular_sucumbencia(frm);
    },
    percentual_sucumbência: function(frm) {
        calcular_sucumbencia(frm);
    },
    honorários_de_sucumbência: function(frm) {
        calcular_totais(frm);
    },
    número_de_parcelas: function(frm) {
        calcular_valores(frm);
    },
    gerar_parcelas: function(frm) {
        gerar_tabela_parcelas(frm);
    },
    validate: function(frm) {
        return validar_tudo(frm);
    }
});

frappe.ui.form.on('Parcela de Honorarios', {
    valor_advogada: function(frm, cdt, cdn) {
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    valor_cliente: function(frm, cdt, cdn) {
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    valor_sucumbência: function(frm, cdt, cdn) {
        recalcular_total_linha(cdt, cdn);
        somar_totais(frm);
    },
    table_ztjx_remove: function(frm) {
        somar_totais(frm);
    },
    table_ztjx_add: function(frm) {
        somar_totais(frm);
    }
});

// === HELPERS ===

function eh_direto(frm) {
    return frm.doc.modo_honorarios === 'Honorários Diretos';
}

function recalcular_total_linha(cdt, cdn) {
    var row = locals[cdt][cdn];
    var total = (row.valor_advogada || 0) + (row.valor_cliente || 0) + (row.valor_sucumbência || 0);
    frappe.model.set_value(cdt, cdn, 'valor_total', total);
}

function controlar_campos(frm) {
    var direto = eh_direto(frm);

    // --- Campos de divisão (ocultos no modo Direto) ---
    var campos_divisao = [
        'tipo_de_cobrança', 'percentual_advogada', 'percentual_cliente',
        'valor_fixo_de_honorarios', 'valor_advogada', 'valor_cliente'
    ];
    campos_divisao.forEach(function(f) {
        frm.set_df_property(f, 'hidden', direto ? 1 : 0);
    });

    // --- Seção Sucumbência (oculta no modo Direto) ---
    frm.set_df_property('sucumbência_section', 'hidden', direto ? 1 : 0);

    // --- Seção Totais: no modo Direto mostra só o total geral ---
    frm.set_df_property('total_advogada', 'label', direto ? 'Total Honorários' : 'Total Advogada');
    frm.set_df_property('total_cliente', 'hidden', direto ? 1 : 0);

    // --- Lógica original dos sub-campos (só quando modo = Acordo com Divisão) ---
    if (!direto) {
        var tipo = frm.doc.tipo_de_cobrança;
        if (tipo === 'Valor fixo') {
            frm.set_df_property('percentual_advogada', 'hidden', 1);
            frm.set_df_property('valor_fixo_de_honorarios', 'hidden', 0);
        } else if (tipo === 'Misto') {
            frm.set_df_property('percentual_advogada', 'hidden', 0);
            frm.set_df_property('valor_fixo_de_honorarios', 'hidden', 0);
        } else {
            frm.set_df_property('percentual_advogada', 'hidden', 0);
            frm.set_df_property('valor_fixo_de_honorarios', 'hidden', 1);
        }

        var tipo_suc = frm.doc.tipo_de_cálculo;
        if (tipo_suc === 'Valor fixo') {
            frm.set_df_property('percentual_sucumbência', 'hidden', 1);
            frm.set_df_property('honorários_de_sucumbência', 'read_only', 0);
        } else {
            frm.set_df_property('percentual_sucumbência', 'hidden', 0);
            frm.set_df_property('honorários_de_sucumbência', 'read_only', 1);
        }
    }
}

function calcular_valores(frm) {
    var total = frm.doc.valor_total_do_acordo || 0;

    if (eh_direto(frm)) {
        // Modo Direto: valor total = honorários integrais
        frm.set_value('valor_advogada', 0);
        frm.set_value('valor_cliente', 0);
        var parcelas = frm.doc.número_de_parcelas || 0;
        if (parcelas > 0) {
            frm.set_value('valor_da_parcela', total / parcelas);
        }
        frm.set_value('total_advogada', total);
        frm.set_value('total_cliente', 0);
        return;
    }

    // Modo Acordo com Divisão (lógica original)
    var tipo = frm.doc.tipo_de_cobrança;
    if (tipo === 'Valor fixo') {
        var fixo = frm.doc.valor_fixo_de_honorarios || 0;
        frm.set_value('valor_advogada', fixo);
        frm.set_value('valor_cliente', total - fixo);
        if (total > 0) {
            frm.set_value('percentual_advogada', (fixo / total) * 100);
            frm.set_value('percentual_cliente', 100 - ((fixo / total) * 100));
        }
    } else if (tipo === 'Misto') {
        var perc_adv = frm.doc.percentual_advogada || 0;
        var fixo = frm.doc.valor_fixo_de_honorarios || 0;
        var valor_perc = total * perc_adv / 100;
        frm.set_value('valor_advogada', valor_perc + fixo);
        frm.set_value('valor_cliente', total - valor_perc - fixo);
        if (total > 0) {
            frm.set_value('percentual_cliente', 100 - perc_adv - ((fixo / total) * 100));
        }
    } else {
        var perc_adv = frm.doc.percentual_advogada || 0;
        frm.set_value('percentual_cliente', 100 - perc_adv);
        frm.set_value('valor_advogada', total * perc_adv / 100);
        frm.set_value('valor_cliente', total * (100 - perc_adv) / 100);
    }
    var parcelas = frm.doc.número_de_parcelas || 0;
    if (parcelas > 0) {
        frm.set_value('valor_da_parcela', (frm.doc.valor_advogada || 0) / parcelas);
    }
    calcular_sucumbencia(frm);
}

function calcular_sucumbencia(frm) {
    if (eh_direto(frm)) return;
    var total = frm.doc.valor_total_do_acordo || 0;
    var tipo_suc = frm.doc.tipo_de_cálculo;
    if (tipo_suc !== 'Valor fixo') {
        var perc_suc = frm.doc.percentual_sucumbência || 0;
        frm.set_value('honorários_de_sucumbência', total * perc_suc / 100);
    }
    calcular_totais(frm);
}

function calcular_totais(frm) {
    if (eh_direto(frm)) {
        frm.set_value('total_advogada', frm.doc.valor_total_do_acordo || 0);
        frm.set_value('total_cliente', 0);
        return;
    }
    var valor_adv = frm.doc.valor_advogada || 0;
    var sucumbencia = frm.doc.honorários_de_sucumbência || 0;
    var valor_cli = frm.doc.valor_cliente || 0;
    frm.set_value('total_advogada', valor_adv + sucumbencia);
    frm.set_value('total_cliente', valor_cli);
}

function gerar_tabela_parcelas(frm) {
    var parcelas = frm.doc.número_de_parcelas || 0;
    var data_inicio = frm.doc.data_primeira_parcela;
    var total = frm.doc.valor_total_do_acordo || 0;
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
        frappe.msgprint('Preencha o valor total do acordo.');
        return;
    }

    if (direto) {
        // Modo Direto: parcelas simples, sem divisão nem sucumbência
        var valor_parcela = total / parcelas;
        frm.clear_table('table_ztjx');
        for (var i = 0; i < parcelas; i++) {
            var dt = frappe.datetime.add_months(data_inicio, i);
            var row = frm.add_child('table_ztjx');
            row.vencimento = dt;
            row.valor_advogada = 0;
            row.valor_cliente = 0;
            row.valor_sucumbência = 0;
            row.valor_total = valor_parcela;
            row.descrição = 'Parcela ' + (i + 1) + ' de ' + parcelas;
            row.status = 'Pendente';
        }
        frm.refresh_field('table_ztjx');
        somar_totais(frm);
        frappe.msgprint(parcelas + ' parcelas geradas com sucesso!');
        return;
    }

    // Modo Acordo com Divisão (lógica original com prompt de sucumbência)
    var valor_adv = frm.doc.valor_advogada || 0;
    var valor_cli = frm.doc.valor_cliente || 0;
    var sucumbencia = frm.doc.honorários_de_sucumbência || 0;

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
        frm.clear_table('table_ztjx');
        for (var i = 0; i < parcelas; i++) {
            var dt = frappe.datetime.add_months(data_inicio, i);
            var row = frm.add_child('table_ztjx');
            row.vencimento = dt;
            row.valor_advogada = parcela_adv;
            row.valor_cliente = parcela_cli;
            row.valor_sucumbência = 0;
            row.descrição = 'Parcela ' + (i + 1) + ' de ' + parcelas;
            row.status = 'Pendente';
            if (values.incluir_sucumbencia === 'Na primeira parcela' && i === 0) {
                row.valor_sucumbência = sucumbencia;
                row.descrição += ' + Sucumbência';
            } else if (values.incluir_sucumbencia === 'Na última parcela' && i === parcelas - 1) {
                row.valor_sucumbência = sucumbencia;
                row.descrição += ' + Sucumbência';
            } else if (values.incluir_sucumbencia === 'Dividir igualmente') {
                row.valor_sucumbência = sucumbencia / parcelas;
            }
            row.valor_total = row.valor_advogada + row.valor_cliente + row.valor_sucumbência;
        }
        frm.refresh_field('table_ztjx');
        somar_totais(frm);
        frappe.msgprint(parcelas + ' parcelas geradas com sucesso!');
    }, 'Como distribuir a sucumbência?', 'Gerar');
}

function somar_totais(frm) {
    if (eh_direto(frm)) {
        var total_parcelas = 0;
        (frm.doc.table_ztjx || []).forEach(function(row) {
            total_parcelas += row.valor_total || 0;
        });
        frm.set_value('total_advogada', total_parcelas || frm.doc.valor_total_do_acordo || 0);
        frm.set_value('total_cliente', 0);
        return;
    }
    var total_adv = 0;
    var total_cli = 0;
    var total_suc = 0;
    (frm.doc.table_ztjx || []).forEach(function(row) {
        total_adv += row.valor_advogada || 0;
        total_cli += row.valor_cliente || 0;
        total_suc += row.valor_sucumbência || 0;
    });
    frm.set_value('total_advogada', total_adv + total_suc);
    frm.set_value('total_cliente', total_cli);
}

function validar_tudo(frm) {
    if (!frm.doc.table_ztjx || frm.doc.table_ztjx.length === 0) return;

    var erros = [];

    if (eh_direto(frm)) {
        // Modo Direto: só valida se soma das parcelas = valor total
        var total_parcelas = 0;
        frm.doc.table_ztjx.forEach(function(row) {
            total_parcelas += row.valor_total || 0;
        });
        var total_acordo = frm.doc.valor_total_do_acordo || 0;
        if (Math.abs(total_parcelas - total_acordo) > 0.02) {
            erros.push('Soma das parcelas (R$ ' + total_parcelas.toFixed(2) +
                ') ≠ Valor Total do Acordo (R$ ' + total_acordo.toFixed(2) + ')');
        }
    } else {
        // Modo Divisão: validação completa
        var total_adv_tabela = 0;
        var total_cli_tabela = 0;
        var total_suc_tabela = 0;
        var total_geral_tabela = 0;
        frm.doc.table_ztjx.forEach(function(row) {
            var soma_linha = (row.valor_advogada || 0) + (row.valor_cliente || 0) + (row.valor_sucumbência || 0);
            var diff = Math.abs(soma_linha - (row.valor_total || 0));
            if (diff > 0.02) {
                erros.push('Parcela ' + row.idx + ': soma (R$ ' + soma_linha.toFixed(2) +
                    ') ≠ Valor Total (R$ ' + (row.valor_total || 0).toFixed(2) + ')');
            }
            if ((row.valor_cliente || 0) < 0) {
                erros.push('Parcela ' + row.idx + ': Valor Cliente negativo (R$ ' + (row.valor_cliente || 0).toFixed(2) + ')');
            }
            total_adv_tabela += row.valor_advogada || 0;
            total_cli_tabela += row.valor_cliente || 0;
            total_suc_tabela += row.valor_sucumbência || 0;
            total_geral_tabela += row.valor_total || 0;
        });
        var valor_adv_esperado = frm.doc.valor_advogada || 0;
        var valor_cli_esperado = frm.doc.valor_cliente || 0;
        var suc_esperada = frm.doc.honorários_de_sucumbência || 0;
        var total_esperado = valor_adv_esperado + valor_cli_esperado + suc_esperada;
        if (Math.abs(total_adv_tabela - valor_adv_esperado) > 0.02) {
            erros.push('Soma Advogada parcelas (R$ ' + total_adv_tabela.toFixed(2) +
                ') ≠ formulário (R$ ' + valor_adv_esperado.toFixed(2) + ')');
        }
        if (Math.abs(total_cli_tabela - valor_cli_esperado) > 0.02) {
            erros.push('Soma Cliente parcelas (R$ ' + total_cli_tabela.toFixed(2) +
                ') ≠ formulário (R$ ' + valor_cli_esperado.toFixed(2) + ')');
        }
        if (Math.abs(total_suc_tabela - suc_esperada) > 0.02) {
            erros.push('Soma Sucumbência parcelas (R$ ' + total_suc_tabela.toFixed(2) +
                ') ≠ formulário (R$ ' + suc_esperada.toFixed(2) + ')');
        }
        if (Math.abs(total_geral_tabela - total_esperado) > 0.02) {
            erros.push('Soma total parcelas (R$ ' + total_geral_tabela.toFixed(2) +
                ') ≠ Total esperado (R$ ' + total_esperado.toFixed(2) + ')');
        }
    }

    if (erros.length > 0) {
        frappe.msgprint({
            title: 'Erro de validação',
            indicator: 'red',
            message: '<strong>Corrija os seguintes problemas:</strong><br><br>' +
                erros.join('<br><br>')
        });
        frappe.validated = false;
    }
}
