frappe.ui.form.on("Document Template", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.set_intro(
				__(
					"Use placeholders no formato <code>{{ nome_do_campo }}</code> no arquivo .docx. Clique em <b>Ver Placeholders Disponíveis</b> para a lista completa."
				),
				"blue"
			);
		}
	},
	ver_placeholders(frm) {
		frappe.call({
			method: "advocacia.advocacia.documentos.get_placeholders_referencia",
			freeze: true,
			freeze_message: __("Carregando placeholders..."),
			callback(r) {
				if (!r.message) {
					return;
				}
				window.advocacia_render_placeholders_referencia(r.message);
			},
		});
	},
});
