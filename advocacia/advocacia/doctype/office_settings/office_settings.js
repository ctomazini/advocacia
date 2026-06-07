frappe.ui.form.on("Office Settings", {
	refresh(frm) {
		if (!window.AdvocaciaMasks) {
			return;
		}
		AdvocaciaMasks.bindMask(frm, "cnpj", AdvocaciaMasks.applyCNPJ, "cnpj");
		if (frm.doc.cnpj) {
			AdvocaciaMasks.formatFormField(frm, "cnpj", AdvocaciaMasks.applyCNPJ);
		}
	},
});
