frappe.ui.form.on("Servico", {
	refresh: function (frm) {
		aplicar_mascara_processo_servico(frm);

		if (frm.is_new()) return;

		frm.add_custom_button("+ Honorários", function () {
			frappe.new_doc("Acordo de Honorarios Processuais", {
				servico: frm.doc.name,
				cliente: frm.doc.cliente,
			});
		}, "Criar");

		frm.add_custom_button("+ Prazo", function () {
			frappe.new_doc("Controle de Prazos", {
				servico: frm.doc.name,
			});
		}, "Criar");

		frm.add_custom_button("+ Audiência", function () {
			frappe.new_doc("Audiencia", {
				servico: frm.doc.name,
			});
		}, "Criar");

		frm.add_custom_button(__("Gerar Documento"), function () {
			frappe.call({
				method: "advocacia.advocacia.documentos.get_templates_disponiveis",
				callback: function (r) {
					if (!r.message || r.message.length === 0) {
						frappe.msgprint(
							__(
								"Nenhum template cadastrado. Va em Template Documento para cadastrar."
							)
						);
						return;
					}
					var d = new frappe.ui.Dialog({
						title: __("Selecionar Template"),
						fields: [
							{
								fieldname: "template",
								fieldtype: "Link",
								label: __("Template"),
								options: "Template Documento",
								reqd: 1,
								get_query: function () {
									return { filters: { habilitado: 1 } };
								},
							},
						],
						primary_action_label: __("Gerar"),
						primary_action: function (values) {
							d.hide();
							frappe.call({
								method: "advocacia.advocacia.documentos.gerar_documento",
								args: {
									servico_name: frm.doc.name,
									template_name: values.template,
								},
								freeze: true,
								freeze_message: __("Gerando documento..."),
								callback: function (res) {
									if (res.message) {
										frappe.msgprint({
											title: __("Documento Gerado"),
											message:
												__("Arquivo: ") +
												res.message.file_name +
												'<br><br><a href="' +
												res.message.file_url +
												'" target="_blank" class="btn btn-primary btn-sm">' +
												__("Baixar Documento") +
												"</a>",
											indicator: "green",
										});
										frm.reload_doc();
									}
								},
							});
						},
					});
					d.show();
				},
			});
		}, __("Documentos"));
	},
	tipo: function (frm) {
		aplicar_mascara_processo_servico(frm);
	},
	numeracao_legada: function (frm) {
		aplicar_mascara_processo_servico(frm);
	},
	numero_processo: function (frm) {
		if (window.AdvocaciaMasks) {
			AdvocaciaMasks.formatFormField(
				frm,
				"numero_processo",
				AdvocaciaMasks.applyCNJ
			);
		}
	},
});

function aplicar_mascara_processo_servico(frm) {
	if (window.AdvocaciaMasks) {
		AdvocaciaMasks.setupServicoProcessoMask(frm);
	}
}

function servico_quick_entry_pseudo_form(dialog) {
	return {
		fields_dict: dialog.fields_dict,
		doc: dialog.doc,
		set_value: function (fieldname, value) {
			dialog.doc[fieldname] = value;
			if (dialog.fields_dict[fieldname]) {
				dialog.fields_dict[fieldname].set_value(value);
			}
		},
	};
}

function setup_servico_quick_entry_masks(dialog) {
	if (!window.AdvocaciaMasks) return;
	const pseudo = servico_quick_entry_pseudo_form(dialog);
	AdvocaciaMasks.setupServicoProcessoMask(pseudo);

	["tipo", "numeracao_legada", "numero_processo"].forEach(function (fieldname) {
		const field = dialog.fields_dict[fieldname];
		if (!field || !field.$input) return;
		field.$input.off("change.servico_qe").on("change.servico_qe", function () {
			setTimeout(function () {
				AdvocaciaMasks.setupServicoProcessoMask(servico_quick_entry_pseudo_form(dialog));
			}, 50);
		});
	});
}

frappe.ui.form.ServicoQuickEntryForm = class ServicoQuickEntryForm extends (
	frappe.ui.form.QuickEntryForm
) {
	render_dialog() {
		super.render_dialog();
		setup_servico_quick_entry_masks(this);
	}
};
