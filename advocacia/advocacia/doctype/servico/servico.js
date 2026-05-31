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
