frappe.listview_settings["Pagamento"] = {
	add_fields: ["status", "data_vencimento", "cliente", "servico", "valor"],
	get_indicator(doc) {
		if (doc.status === "Vencido") {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.status === "Recebido" || doc.status === "Repassado") {
			return [__(doc.status), "green", "status,=," + doc.status];
		}
		if (doc.status === "Pendente" && doc.data_vencimento) {
			const hoje = frappe.datetime.get_today();
			const diff = frappe.datetime.get_day_diff(doc.data_vencimento, hoje);
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

		listview.page.add_inner_button(__("Vencidos"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([[listview.doctype, "status", "=", "Vencido"]]);
		});

		listview.page.add_inner_button(__("Próximos 7 dias"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([
				[listview.doctype, "status", "=", "Pendente"],
				[listview.doctype, "data_vencimento", "between", [hoje, sete]],
			]);
		});

		listview.page.add_inner_button(__("Recebidos hoje"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([
				[listview.doctype, "status", "in", ["Recebido", "Repassado"]],
				[listview.doctype, "data_recebimento", "=", hoje],
			]);
		});

		function executar_bulk_delete(names, done) {
			frappe.call({
				method: "advocacia.advocacia.financeiro.bulk_delete_pagamentos",
				args: { names: names },
				freeze: true,
				freeze_message: __("Excluindo {0} pagamento(s)...", [names.length]),
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
						msg += __("<b>{0}</b> pagamento(s) excluído(s).", [res.excluidos.length]);
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

		listview.bulk_operations.delete = function (docnames, done) {
			const names = docnames.map((name) => name.toString());

			if (names.length >= 5) {
				const d = new frappe.ui.Dialog({
					title: __("Confirmar Exclusão em Massa"),
					fields: [
						{
							fieldtype: "HTML",
							options:
								'<p style="margin-bottom:10px;">' +
								__("Você está prestes a excluir <b>{0} pagamentos</b>.", [names.length]) +
								"<br>" +
								__("Pagamentos com status Recebido, Repassado ou Vencido serão ignorados.") +
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
					"Excluir {0} pagamento(s)? Recebidos, Repassados e Vencidos serão ignorados.",
					[names.length]
				),
				function () {
					executar_bulk_delete(names, done);
				}
			);
		};
	},
};
