frappe.ui.form.on('Audiencia', {
    refresh(frm) {
        // Botão "Entrar" para audiências virtuais com link
        if (frm.doc.modalidade === 'Virtual' && frm.doc.link_virtual) {
            frm.add_custom_button(__('🖥️ Entrar na Audiência'), function() {
                window.open(frm.doc.link_virtual, '_blank');
            }).addClass('btn-primary');
        }
    },
    modalidade(frm) {
        if (frm.doc.modalidade !== 'Virtual') {
            frm.set_value('link_virtual', '');
        }
    }
});
