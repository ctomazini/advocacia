frappe.ui.form.on('Fee Installment', {
    refresh: function(frm) {
        const cores = {
            'Pendente': 'orange',
            'Vencido': 'red',
            'Recebido': 'green',
            'Repassado': 'blue',
            'Cancelado': 'gray'
        };
        frm.page.set_indicator(frm.doc.status, cores[frm.doc.status] || 'gray');

        if (frm.is_new()) return;

        // Botão Registrar Recebimento
        if (!frm.doc.received_date && frm.doc.status !== 'Cancelado') {
            var valor_receb = frm.doc.total_amount || frm.doc.lawyer_amount || 0;
            frm.add_custom_button('✓ Registrar Recebimento', function() {
                frappe.confirm(
                    `Confirmar recebimento de <b>R$ ${frappe.format(valor_receb, {fieldtype:'Currency'})}</b> hoje?`,
                    function() {
                        frappe.call({
                            method: 'registrar_recebimento',
                            doc: frm.doc,
                            callback: function(r) {
                                frm.reload_doc();
                                frappe.show_alert({message: '✓ Recebimento registrado!', indicator: 'green'});
                            }
                        });
                    }
                );
            }, 'primary');
        }

        // Botão Registrar Repasse (só se tem valor cliente e já recebeu)
        if (frm.doc.received_date && frm.doc.client_amount > 0 && !frm.doc.transfer_date) {
            frm.add_custom_button('↗ Registrar Repasse ao Cliente', function() {
                frappe.confirm(
                    `Confirmar repasse de <b>R$ ${frappe.format(frm.doc.client_amount, {fieldtype:'Currency'})}</b> ao cliente hoje?`,
                    function() {
                        frappe.call({
                            method: 'registrar_repasse',
                            doc: frm.doc,
                            callback: function(r) {
                                frm.reload_doc();
                                frappe.show_alert({message: '✓ Repasse registrado!', indicator: 'blue'});
                            }
                        });
                    }
                );
            });
        }
    }
});
