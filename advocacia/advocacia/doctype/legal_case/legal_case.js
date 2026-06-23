frappe.ui.form.on("Legal Case", {
	refresh(frm) {
		aplicar_mascara_processo_servico(frm);
		setup_legal_case_form_intro(frm);

		if (frm.is_new()) {
			return;
		}

		if (frm.dashboard?.wrapper) {
			$(frm.dashboard.wrapper).hide();
		}
		frm.$wrapper?.find(".form-dashboard-section, .form-dashboard, .form-links").hide();

		frm.add_custom_button("+ Cobrança de Honorários", () => {
			frappe.new_doc("Fee Agreement", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		}, __("Criar"));

		frm.add_custom_button("+ Prazo", () => {
			frappe.new_doc("Deadline", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		}, __("Criar"));

		frm.add_custom_button("+ Audiência", () => {
			frappe.new_doc("Hearing", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		}, __("Criar"));

		frm.add_custom_button(__("Gerar Documentos"), () => {
			advocacia.openGenerateDocumentsDialog(frm);
		}, __("Documentos"));

		if (window.advocacia?.hub?.load) {
			advocacia.hub.load(frm);
		}
	},
	type(frm) {
		aplicar_mascara_processo_servico(frm);
	},
	legacy_numbering(frm) {
		aplicar_mascara_processo_servico(frm);
	},
	case_number(frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(frm, "case_number", AdvocaciaMasks.applyCNJ);
		}
	},
});

function setup_legal_case_form_intro(frm) {
	if (!frm.is_new()) {
		return;
	}
	frm.set_intro(
		__(
			"O número CNJ e os cadastros judiciais (Comarca, Vara, Tribunal) podem ser preenchidos depois. Consultorias e diligências não exigem CNJ."
		),
		"blue"
	);
}

function aplicar_mascara_processo_servico(frm) {
	if (window.AdvocaciaMasks) {
		AdvocaciaMasks.setupLegalCaseProcessoMask(frm);
	}
}

function legal_case_quick_entry_pseudo_form(dialog) {
	return {
		fields_dict: dialog.fields_dict,
		doc: dialog.doc,
		set_value(fieldname, value) {
			dialog.doc[fieldname] = value;
			if (dialog.fields_dict[fieldname]) {
				dialog.fields_dict[fieldname].set_value(value);
			}
		},
	};
}

function setup_legal_case_quick_entry_masks(dialog) {
	if (!window.AdvocaciaMasks) {
		return;
	}
	const pseudo = legal_case_quick_entry_pseudo_form(dialog);
	AdvocaciaMasks.setupLegalCaseProcessoMask(pseudo);

	["type", "legacy_numbering", "case_number"].forEach((fieldname) => {
		const field = dialog.fields_dict[fieldname];
		if (!field || !field.$input) {
			return;
		}
		field.$input.off("change.legal_case_qe").on("change.legal_case_qe", () => {
			setTimeout(() => {
				AdvocaciaMasks.setupLegalCaseProcessoMask(
					legal_case_quick_entry_pseudo_form(dialog)
				);
			}, 50);
		});
	});
}

frappe.ui.form.LegalCaseQuickEntryForm = class LegalCaseQuickEntryForm extends (
	frappe.ui.form.QuickEntryForm
) {
	render_dialog() {
		super.render_dialog();
		setup_legal_case_quick_entry_masks(this);
	}
};
