frappe.ui.form.on("Office Settings", {
	refresh(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.setupOfficeSettingsForm(frm);
		}
	},
	cnpj(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(frm, "cnpj", AdvocaciaMasks.applyCNPJ);
		}
	},
});
