frappe.ui.form.on('Legal Task', {
    refresh: function(frm) {
        setup_legal_task_form_intro(frm);
        const cores = {
            'Pendente': 'orange',
            'Em Andamento': 'blue',
            'Concluída': 'green',
            'Cancelada': 'gray'
        };
        frm.page.set_indicator(frm.doc.status, cores[frm.doc.status] || 'gray');

        if (frm.is_new()) return;

        if (frm.doc.status !== 'Concluída' && frm.doc.status !== 'Cancelada') {
            frm.add_custom_button('✓ Concluir', function() {
                frappe.call({
                    method: 'concluir',
                    doc: frm.doc,
                    callback: function(r) {
                        frm.reload_doc();
                        frappe.show_alert({message: '✓ Tarefa concluída!', indicator: 'green'});
                    }
                });
            }, 'primary');
        }
    }
});

function setup_legal_task_form_intro(frm) {
    frm.set_intro(
        __(
            "<strong>Tarefa interna</strong> — atividade operacional do escritório (ligar, revisar, protocolar internamente). O processo é opcional.<br><br>Não confundir com <strong>Prazo</strong>, que é data fatal do judiciário com consequência processual."
        ),
        "blue"
    );
}
