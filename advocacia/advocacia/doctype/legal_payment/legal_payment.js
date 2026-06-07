frappe.ui.form.on("Legal Payment", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status === "Cancelado") {
			frm.set_read_only();
			const intro =
				frm.doc.tipo_origem === "Atos Advocatícios"
					? __(
							"Legal Payment cancelado — registro imutável. Os atos foram liberados; você pode excluir este pagamento se desejar."
					  )
					: __(
							"Legal Payment cancelado — registro imutável. A parcela no acordo foi atualizada; você pode excluir este pagamento se desejar."
					  );
			frm.set_intro(intro, "blue");
			return;
		}

		if (frm.doc.tipo_origem === "Atos Advocatícios") {
			configurar_botoes_atos(frm);
		} else {
			configurar_botoes_honorarios(frm);
		}
	},
});

function configurar_botoes_atos(frm) {
	if (frm.doc.service_record) {
		frm.add_custom_button(__("Ver Service Record"), function () {
			frappe.set_route("Form", "Service Record", frm.doc.service_record);
		});
	}

	if (["Pendente", "Vencido"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Cancelar Legal Payment"), function () {
			frappe.confirm(
				__(
					"Cancelar este pagamento e liberar os atos vinculados para nova cobrança?<br><br>Os atos voltam para <strong>Pendente</strong>."
				),
				function () {
					frappe.call({
						method: "advocacia.advocacia.financeiro.cancelar_cobranca_pagamento_atos",
						args: { pagamento_name: frm.doc.name },
						freeze: true,
						freeze_message: __("Cancelando pagamento..."),
						callback: function (r) {
							if (!r.message) {
								return;
							}
							frappe.show_alert({
								message: __("Legal Payment cancelado. Atos liberados."),
								indicator: "green",
							});
							frm.reload_doc();
						},
					});
				}
			);
		}).addClass("btn-danger");
	}
}

function configurar_botoes_honorarios(frm) {
	if (frm.doc.fee_agreement) {
		frm.add_custom_button(__("Ver Acordo"), function () {
			frappe.set_route("Form", "Fee Agreement", frm.doc.fee_agreement);
		});
	}

	if (["Pendente", "Vencido"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Marcar como Recebido"), function () {
			frappe.confirm(__("Marcar este pagamento como recebido hoje?"), function () {
				frappe.call({
					method: "advocacia.advocacia.painel_api.marcar_parcela_recebida",
					args: { parcela_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Registrando recebimento..."),
					callback: function () {
						frappe.show_alert({
							message: __("Legal Payment marcado como recebido."),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
		}).addClass("btn-primary-dark");
	}

	if (["Pendente", "Vencido", "Recebido", "Repassado"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Cancelar Legal Payment"), function () {
			const msg_recebido =
				frm.doc.status === "Recebido" || frm.doc.status === "Repassado"
					? __(
							"Cancelar pagamento já recebido? A parcela no acordo voltará para <strong>Cancelado</strong> e o acordo deixará de constar como quitado se aplicável."
					  )
					: __(
							"Cancelar este pagamento? A parcela correspondente no acordo será marcada como <strong>Cancelado</strong>."
					  );

			frappe.confirm(msg_recebido, function () {
				frappe.call({
					method: "advocacia.advocacia.financeiro.cancelar_pagamento_honorarios",
					args: { pagamento_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Cancelando pagamento..."),
					callback: function (r) {
						if (!r.message) {
							return;
						}
						frappe.show_alert({
							message: __("Legal Payment cancelado."),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
		}).addClass("btn-danger");
	}
}
