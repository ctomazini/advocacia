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
	show_placeholders(frm) {
		advocacia.openPlaceholdersReference();
	},
});
