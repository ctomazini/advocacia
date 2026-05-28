frappe.ui.form.on('Servico', {
    refresh: function(frm) {
        if (frm.is_new()) return;

        frm.add_custom_button('+ Honorários', function() {
            frappe.new_doc('Acordo de Honorarios Processuais', {
                servico: frm.doc.name,
                cliente: frm.doc.cliente
            });
        }, 'Criar');

        frm.add_custom_button('+ Prazo', function() {
            frappe.new_doc('Controle de Prazos', {
                servico: frm.doc.name
            });
        }, 'Criar');

        frm.add_custom_button('+ Audiência', function() {
            frappe.new_doc('Audiencia', {
                servico: frm.doc.name
            });
        }, 'Criar');
    }
});
