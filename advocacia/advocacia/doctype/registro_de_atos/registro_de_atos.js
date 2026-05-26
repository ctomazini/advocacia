
frappe.ui.form.on('Registro de Atos', {
    refresh: function(frm) {
        calcular_totais_atos(frm);
        atualizar_status(frm);
    },
    gerar_cobranca: function(frm) {
        gerar_cobranca_atos(frm);
    }
});

frappe.ui.form.on('Ato Advocaticio', {
    valor: function(frm) {
        calcular_totais_atos(frm);
    },
    status: function(frm) {
        calcular_totais_atos(frm);
        atualizar_status(frm);
    },
    atos_add: function(frm) {
        calcular_totais_atos(frm);
    },
    atos_remove: function(frm) {
        calcular_totais_atos(frm);
        atualizar_status(frm);
    }
});

function calcular_totais_atos(frm) {
    var pendente = 0;
    var cobrado = 0;
    (frm.doc.atos || []).forEach(function(row) {
        if (row.status === 'Pendente') {
            pendente += row.valor || 0;
        } else if (row.status === 'Cobrado') {
            cobrado += row.valor || 0;
        }
    });
    frm.set_value('total_pendente', pendente);
    frm.set_value('total_cobrado', cobrado);
    frm.set_value('total_geral', pendente + cobrado);
}

function atualizar_status(frm) {
    if (!frm.doc.atos || frm.doc.atos.length === 0) {
        frm.set_value('status', 'Em aberto');
        return;
    }
    var tem_pendente = false;
    var tem_cobrado = false;
    (frm.doc.atos || []).forEach(function(row) {
        if (row.status === 'Pendente') tem_pendente = true;
        if (row.status === 'Cobrado') tem_cobrado = true;
    });
    if (tem_pendente && tem_cobrado) {
        frm.set_value('status', 'Parcialmente cobrado');
    } else if (!tem_pendente && tem_cobrado) {
        frm.set_value('status', 'Cobrado');
    } else {
        frm.set_value('status', 'Em aberto');
    }
}

function gerar_cobranca_atos(frm) {
    if (!frm.doc.atos || frm.doc.atos.length === 0) {
        frappe.msgprint('Não há atos cadastrados.');
        return;
    }
    var pendentes = [];
    (frm.doc.atos || []).forEach(function(row) {
        if (row.status === 'Pendente' && (row.valor || 0) > 0) {
            pendentes.push(row);
        }
    });
    if (pendentes.length === 0) {
        frappe.msgprint('Não há atos pendentes para cobrar.');
        return;
    }
    var total = 0;
    var descricao_itens = [];
    pendentes.forEach(function(row) {
        total += row.valor || 0;
        descricao_itens.push(row.tipo + ': ' + (row.descrição || '') + ' (R$ ' + (row.valor || 0).toFixed(2) + ')');
    });
    frappe.confirm(
        '<strong>Gerar cobrança de ' + pendentes.length + ' ato(s) pendente(s)?</strong><br><br>' +
        descricao_itens.join('<br>') +
        '<br><br><strong>Total: R$ ' + total.toFixed(2) + '</strong>',
        function() {
            frappe.call({
                method: 'gerar_faturas_atos',
                args: { registro_name: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint('Fatura criada com sucesso! Total: R$ ' + r.message.total.toFixed(2));
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}
