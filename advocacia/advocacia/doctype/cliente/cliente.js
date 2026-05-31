frappe.ui.form.on("Cliente", {
	refresh(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.setupClienteForm(frm);
		}
	},
	tipo_pessoa(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.setupClienteForm(frm);
		}
	},
	cpf(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(frm, "cpf", AdvocaciaMasks.applyCPF);
		}
	},
	cnpj(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(frm, "cnpj", AdvocaciaMasks.applyCNPJ);
		}
	},
	cpf_representante(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(
				frm,
				"cpf_representante",
				AdvocaciaMasks.applyCPF
			);
		}
	},
});

frappe.ui.form.on("Contato Cliente", {
	form_render(frm) {
		if (!window.AdvocaciaMasks) return;
		AdvocaciaMasks.bindMask(frm, "telefone", AdvocaciaMasks.applyPhone, "fixo");
		AdvocaciaMasks.bindMask(frm, "celular", AdvocaciaMasks.applyPhone, "celular");
	},
	telefone(frm, cdt, cdn) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatChildField(
				cdt,
				cdn,
				"telefone",
				AdvocaciaMasks.applyPhone
			);
		}
	},
	celular(frm, cdt, cdn) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatChildField(
				cdt,
				cdn,
				"celular",
				AdvocaciaMasks.applyPhone
			);
		}
	},
});

frappe.ui.form.on("Endereco Cliente", {
	form_render(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.bindMask(frm, "cep", AdvocaciaMasks.applyCEP, "cep");
		}
	},
	cep(frm, cdt, cdn) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatChildField(cdt, cdn, "cep", AdvocaciaMasks.applyCEP);
		}
	},
});
