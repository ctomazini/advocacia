frappe.ui.form.on("Deadline", {
	refresh(frm) {
		setup_deadline_form_intro(frm);
	},
});

function setup_deadline_form_intro(frm) {
	frm.set_intro(
		__(
			"<strong>Prazo processual</strong> — data fatal imposta pelo judiciário (contestação, recurso, manifestação). Aparece no Painel e gera alertas.<br><br>Não confundir com <strong>Tarefa</strong>, que é atividade interna do escritório sem consequência processual automática."
		),
		"blue"
	);
}
