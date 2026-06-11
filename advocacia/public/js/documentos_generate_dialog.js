/* Diálogo de geração .docx — disponível globalmente (hub + toolbar do Legal Case). */
(function () {
	window.advocacia = window.advocacia || {};

	function atualizar_label_botao_bulk(dialog) {
		const total = dialog.$wrapper.find(".adv-doc-template:checked").length;
		dialog.set_primary_action(
			total ? __("Gerar {0} documento(s)", [total]) : __("Gerar documentos")
		);
	}

	function gerar_documentos_em_lote(frm, template_names) {
		frappe.call({
			method: "advocacia.advocacia.documentos.gerar_documentos_em_lote",
			args: {
				servico_name: frm.doc.name,
				template_names,
			},
			freeze: true,
			freeze_message: __("Gerando documentos..."),
			callback(r) {
				if (!r.message || !r.message.data) {
					return;
				}
				const data = r.message.data;
				let html = "";

				if (data.gerados && data.gerados.length) {
					html += "<p><strong>" + __("Documentos gerados:") + "</strong></p><ul>";
					data.gerados.forEach((item) => {
						html +=
							"<li>" +
							frappe.utils.escape_html(item.title || item.template) +
							' — <a href="' +
							item.file_url +
							'" target="_blank">' +
							frappe.utils.escape_html(item.file_name) +
							"</a></li>";
					});
					html += "</ul>";
				}

				if (data.falhas && data.falhas.length) {
					html += "<p><strong>" + __("Falhas:") + "</strong></p><ul>";
					data.falhas.forEach((item) => {
						html +=
							"<li>" +
							frappe.utils.escape_html(item.template) +
							": " +
							frappe.utils.escape_html(item.erro) +
							"</li>";
					});
					html += "</ul>";
				}

				frappe.msgprint({
					title: __("Geração em lote"),
					message: html || __("Nenhum documento gerado."),
					indicator: data.falhas && data.falhas.length ? "orange" : "green",
					wide: true,
				});
				frm.reload_doc();
			},
		});
	}

	function montar_dialog_gerar_documentos(frm, templates, kits) {
		const agrupados = {};
		templates.forEach((tpl) => {
			const tipo = tpl.document_type || __("Outro");
			if (!agrupados[tipo]) {
				agrupados[tipo] = [];
			}
			agrupados[tipo].push(tpl);
		});

		let checklist_html =
			'<div class="adv-doc-bulk-list" style="max-height:320px;overflow-y:auto;">';
		checklist_html +=
			'<p class="text-muted small">' +
			__("Selecione os templates ou use um kit para pré-marcar.") +
			"</p>";
		checklist_html +=
			'<p><label class="checkbox"><input type="checkbox" class="adv-doc-select-all"> ' +
			__("Selecionar todos") +
			"</label></p>";

		Object.keys(agrupados)
			.sort()
			.forEach((tipo) => {
				checklist_html +=
					'<div style="margin-top:10px;font-weight:600;">' +
					frappe.utils.escape_html(tipo) +
					"</div>";
				agrupados[tipo].forEach((tpl) => {
					checklist_html +=
						'<p style="margin:4px 0 4px 12px;">' +
						'<label class="checkbox">' +
						'<input type="checkbox" class="adv-doc-template" data-template="' +
						frappe.utils.escape_html(tpl.name) +
						'"> ' +
						frappe.utils.escape_html(tpl.title) +
						"</label></p>";
				});
			});
		checklist_html += "</div>";

		const dialog = new frappe.ui.Dialog({
			title: __("Gerar Documentos"),
			fields: [
				{
					fieldname: "kit",
					fieldtype: "Select",
					label: __("Kit (opcional)"),
					options: ["", ...kits.map((k) => k.name)],
					description: __("Pré-seleciona os templates de um kit"),
				},
				{
					fieldname: "templates_html",
					fieldtype: "HTML",
					options: checklist_html,
				},
			],
			secondary_action_label: __("Ver placeholders"),
			secondary_action() {
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
			primary_action_label: __("Gerar documentos"),
			primary_action() {
				const selecionados = [];
				dialog.$wrapper.find(".adv-doc-template:checked").each(function () {
					selecionados.push($(this).attr("data-template"));
				});
				if (!selecionados.length) {
					frappe.msgprint(__("Selecione ao menos um template."));
					return;
				}
				dialog.hide();
				gerar_documentos_em_lote(frm, selecionados);
			},
		});

		dialog.show();

		if (dialog.fields_dict.kit && kits.length) {
			dialog.fields_dict.kit.df.options = ["", ...kits.map((k) => k.name)];
			dialog.fields_dict.kit.refresh();
			dialog.fields_dict.kit.$input.on("change", function () {
				const kit_name = dialog.get_value("kit");
				dialog.$wrapper.find(".adv-doc-template").prop("checked", false);
				if (!kit_name) {
					atualizar_label_botao_bulk(dialog);
					return;
				}
				const kit = kits.find((k) => k.name === kit_name);
				if (!kit || !kit.templates) {
					return;
				}
				kit.templates.forEach((template_name) => {
					dialog.$wrapper
						.find('.adv-doc-template[data-template="' + template_name + '"]')
						.prop("checked", true);
				});
				atualizar_label_botao_bulk(dialog);
			});
		} else if (dialog.fields_dict.kit) {
			dialog.toggle_display("kit", false);
		}

		dialog.$wrapper.find(".adv-doc-select-all").on("change", function () {
			const checked = $(this).is(":checked");
			dialog.$wrapper.find(".adv-doc-template").prop("checked", checked);
			atualizar_label_botao_bulk(dialog);
		});

		dialog.$wrapper.on("change", ".adv-doc-template", function () {
			atualizar_label_botao_bulk(dialog);
		});

		atualizar_label_botao_bulk(dialog);
	}

	function abrir_dialog_gerar_documentos(frm) {
		if (!frm || frm.is_new() || !frm.doc?.name) {
			frappe.msgprint(__("Salve o serviço antes de gerar documentos."));
			return;
		}

		frappe.call({
			method: "advocacia.advocacia.documentos.get_templates_disponiveis",
			callback(r_templates) {
				const templates = r_templates.message || [];
				if (!templates.length) {
					frappe.msgprint(
						__(
							"Nenhum template cadastrado. Vá em Document Template para cadastrar."
						)
					);
					return;
				}

				frappe.call({
					method: "advocacia.advocacia.documentos.get_kits_disponiveis",
					callback(r_kits) {
						montar_dialog_gerar_documentos(frm, templates, r_kits.message || []);
					},
				});
			},
		});
	}

	advocacia.openGenerateDocumentsDialog = abrir_dialog_gerar_documentos;
	window.abrir_dialog_gerar_documentos = abrir_dialog_gerar_documentos;
})();
