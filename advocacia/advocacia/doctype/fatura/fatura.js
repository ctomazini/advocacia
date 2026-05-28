frappe.ui.form.on('Fatura', {
    refresh: function(frm) {
        if (frm.doc.status !== 'Paga' && frm.doc.status !== 'Cancelada' && !frm.is_new()) {
            frm.add_custom_button('✓ Registrar Pagamento', function() {
                frappe.confirm(
                    `Confirmar pagamento de <b>${format_currency(frm.doc.valor)}</b> hoje (${frappe.datetime.get_today()})?`,
                    function() {
                        frappe.call({
                            method: 'registrar_pagamento',
                            doc: frm.doc,
                            callback: function(r) {
                                frm.reload_doc();
                                frappe.show_alert({message: '✓ Pagamento registrado!', indicator: 'green'});
                            }
                        });
                    }
                );
            }, 'primary');
        }

        const cores = {'Pendente': 'orange', 'Paga': 'green', 'Vencida': 'red', 'Cancelada': 'gray'};
        frm.page.set_indicator(frm.doc.status, cores[frm.doc.status] || 'gray');
    },

    data_pagamento: function(frm) {
        if (frm.doc.data_pagamento) {
            frm.set_value('status', 'Paga');
        } else {
            const hoje = frappe.datetime.get_today();
            if (frm.doc.data_vencimento && frm.doc.data_vencimento < hoje) {
                frm.set_value('status', 'Vencida');
            } else {
                frm.set_value('status', 'Pendente');
            }
        }
    }
});
