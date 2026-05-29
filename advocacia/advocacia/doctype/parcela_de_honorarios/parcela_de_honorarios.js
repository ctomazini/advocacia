frappe.ui.form.on('Parcela de Honorarios', {
    refresh: function(frm) {
        const cores = {
            'Pendente': 'orange',
            'Vencida': 'red',
            'Recebida': 'green',
            'Repassada': 'blue',
            'Cancelada': 'gray'
        };
        frm.page.set_indicator(frm.doc.status, cores[frm.doc.status] || 'gray');

        if (frm.is_new()) return;

        // Botão Registrar Recebimento
        if (!frm.doc.data_recebimento && frm.doc.status !== 'Cancelada') {
            var valor_receb = frm.doc.valor_total || frm.doc.valor_advogada || 0;
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
        if (frm.doc.data_recebimento && frm.doc.valor_cliente > 0 && !frm.doc.data_repasse) {
            frm.add_custom_button('↗ Registrar Repasse ao Cliente', function() {
                frappe.confirm(
                    `Confirmar repasse de <b>R$ ${frappe.format(frm.doc.valor_cliente, {fieldtype:'Currency'})}</b> ao cliente hoje?`,
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
