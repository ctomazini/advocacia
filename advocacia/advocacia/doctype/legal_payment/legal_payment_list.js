frappe.listview_settings["Legal Payment"] = {
	hide_name_column: true,
	add_fields: ["status", "due_date", "client", "legal_case", "amount", "origin_type", "fee_agreement", "service_record"],
	formatters: {
		title(value, _df, doc) {
			const subject = value || doc.name || "";
			const meta = [];
			if (doc.due_date) {
				meta.push(__("Venc.") + " " + frappe.datetime.str_to_user(doc.due_date));
			}
			if (doc.amount != null && doc.amount !== "") {
				meta.push(frappe.format_currency(doc.amount));
			}
			if (!meta.length) {
				return subject;
			}
			// List view usa textContent no link — retorno deve ser texto puro (sem HTML).
			return subject + " · " + meta.join(" · ");
		},
		origin_type(value, _df, doc) {
			const origem = (value || "").trim();
			if (!origem) return "";

			if (origem === "Honorários (Parcela)" && doc.fee_agreement) {
				return frappe.utils.get_form_link(
					"Fee Agreement",
					doc.fee_agreement,
					true,
					origem
				);
			}
			if (origem === "Atos Advocatícios" && doc.service_record) {
				return frappe.utils.get_form_link(
					"Service Record",
					doc.service_record,
					true,
					origem
				);
			}

			return frappe.utils.escape_html(origem);
		},
	},
	get_indicator(doc) {
		const hoje = frappe.datetime.get_today();
		if (doc.status === "Vencido") {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.status === "Recebido" || doc.status === "Repassado") {
			return [__(doc.status), "green", "status,=," + doc.status];
		}
		if (doc.status === "Pendente" && doc.due_date) {
			const diff = frappe.datetime.get_day_diff(doc.due_date, hoje);
			if (diff < 0) {
				return [__("Vencido"), "red", "status,=,Vencido"];
			}
			if (diff >= 0 && diff <= 7) {
				return [__("Próximo vencimento"), "orange", "status,=,Pendente"];
			}
		}
		if (doc.status === "Cancelado") {
			return [__("Cancelado"), "gray", "status,=,Cancelado"];
		}
		return [__(doc.status || "Pendente"), "blue", "status,=," + (doc.status || "Pendente")];
	},
	onload(listview) {
		const hoje = frappe.datetime.get_today();
		const sete = frappe.datetime.add_days(hoje, 7);

		function apply_filters(filters) {
			listview.filter_area.clear().then(() => {
				listview.filter_area.add(filters);
			});
		}

		listview.page.add_inner_button(__("Vencidos"), () => {
			apply_filters([[listview.doctype, "status", "=", "Vencido"]]);
		});

		listview.page.add_inner_button(__("Próximos 7 dias"), () => {
			apply_filters([
				[listview.doctype, "status", "=", "Pendente"],
				[listview.doctype, "due_date", "between", [hoje, sete]],
			]);
		});

		listview.page.add_inner_button(__("Recebidos hoje"), () => {
			apply_filters([
				[listview.doctype, "status", "in", ["Recebido", "Repassado"]],
				[listview.doctype, "received_date", "=", hoje],
			]);
		});

		function executar_bulk_delete(names, done) {
			frappe.call({
				method: "advocacia.advocacia.financeiro.bulk_delete_pagamentos",
				args: { names: names },
				freeze: true,
				freeze_message: __("Excluindo {0} recebimento(s)...", [names.length]),
				callback(r) {
					if (!r.message) {
						if (done) {
							done();
						}
						return;
					}

					const res = r.message;
					let msg = "";
					let indicator = "green";

					if (res.excluidos && res.excluidos.length > 0) {
						msg += __("<b>{0}</b> recebimento(s) excluído(s).", [res.excluidos.length]);
						frappe.utils.play_sound("delete");
					}
					if (res.ignorados && res.ignorados.length > 0) {
						indicator = res.excluidos && res.excluidos.length > 0 ? "orange" : "red";
						msg += "<br><br><b>" + __("Ignorados ({0}):", [res.ignorados.length]) + "</b><ul>";
						res.ignorados.forEach(function (ig) {
							msg += "<li>" + frappe.utils.escape_html(ig.name) + ": " + frappe.utils.escape_html(ig.motivo) + "</li>";
						});
						msg += "</ul>";
					}

					frappe.msgprint({ message: msg, title: __("Resultado"), indicator: indicator });
					listview.refresh();
					if (done) {
						done();
					}
				},
			});
		}

		function confirmar_bulk_delete(docnames) {
			const names = docnames.map((name) => name.toString());
			if (!names.length) {
				return;
			}

			const done = () => {
				listview.disable_list_update = false;
				listview.clear_checked_items();
			};

			if (names.length >= 5) {
				const d = new frappe.ui.Dialog({
					title: __("Confirmar Exclusão em Massa"),
					fields: [
						{
							fieldtype: "HTML",
							options:
								'<p style="margin-bottom:10px;">' +
								__("Você está prestes a excluir <b>{0} recebimentos</b>.", [names.length]) +
								"<br>" +
								__("Recebimentos com status Recebido, Repassado ou Vencido serão ignorados.") +
								"</p>" +
								"<p>" +
								__("Digite <b>EXCLUIR</b> para confirmar:") +
								"</p>",
						},
						{
							fieldname: "confirmacao",
							fieldtype: "Data",
							label: __("Confirmação"),
							reqd: 1,
						},
					],
					primary_action_label: __("Excluir"),
					primary_action(values) {
						if (values.confirmacao !== "EXCLUIR") {
							frappe.msgprint({
								message: __("Digite exatamente EXCLUIR para confirmar."),
								indicator: "red",
							});
							return;
						}
						d.hide();
						listview.disable_list_update = true;
						executar_bulk_delete(names, done);
					},
				});

				d.fields_dict.confirmacao.$input.on("input", function () {
					const val = $(this).val();
					d.get_primary_btn().prop("disabled", val !== "EXCLUIR");
				});
				d.get_primary_btn().prop("disabled", true);
				d.show();
				return;
			}

			frappe.confirm(
				__(
					"Excluir {0} recebimento(s)? Recebidos, Repassados e Vencidos serão ignorados.",
					[names.length]
				),
				function () {
					listview.disable_list_update = true;
					executar_bulk_delete(names, done);
				}
			);
		}

		const delete_label = __("Delete", null, "Button in list view actions menu");
		const delete_item = listview.actions_menu_items.find((item) => item.label === delete_label);
		if (delete_item) {
			delete_item.action = () => confirmar_bulk_delete(listview.get_checked_items(true));
			listview.page.clear_actions_menu();
			listview.set_actions_menu_items();
		}
	},
};
