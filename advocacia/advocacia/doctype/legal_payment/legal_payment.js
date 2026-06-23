frappe.ui.form.on("Legal Payment", {
	refresh(frm) {
		if (frm.is_new()) {
			setup_legal_payment_form_intro(frm);
			return;
		}

		if (frm.doc.status === "Cancelado") {
			frm.set_read_only();
			const intro =
				frm.doc.origin_type === "Atos Advocatícios"
					? __(
							"Recebimento cancelado — registro imutável. Os atos foram liberados; você pode excluir este recebimento se desejar."
					  )
					: __(
							"Recebimento cancelado — registro imutável. A parcela em honorários foi atualizada; você pode excluir este recebimento se desejar."
					  );
			frm.set_intro(intro, "blue");
			return;
		}

		if (frm.doc.origin_type === "Atos Advocatícios") {
			configurar_botoes_atos(frm);
		} else {
			setup_legal_payment_form_intro(frm);
			configurar_botoes_honorarios(frm);
		}
	},
});

function setup_legal_payment_form_intro(frm) {
	frm.set_intro(
		__(
			"Este registro representa uma parcela a receber (ou já recebida) do cliente. Origem: gerado automaticamente por Contrato de Honorários ou Cobrança de Serviço, ou criado manualmente para entradas avulsas."
		),
		"blue"
	);
}

function configurar_botoes_atos(frm) {
	if (frm.doc.service_record) {
		frm.add_custom_button(__("Ver Cobrança de Serviço"), function () {
			frappe.set_route("Form", "Service Record", frm.doc.service_record);
		});
	}

	if (["Pendente", "Vencido"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Cancelar Recebimento"), function () {
			frappe.confirm(
				__(
					"Cancelar este recebimento e liberar os atos vinculados para nova cobrança?<br><br>Os atos voltam para <strong>Pendente</strong>."
				),
				function () {
					frappe.call({
						method: "advocacia.advocacia.financeiro.cancelar_cobranca_pagamento_atos",
						args: { pagamento_name: frm.doc.name },
						freeze: true,
						freeze_message: __("Cancelando recebimento..."),
						callback: function (r) {
							if (!r.message) {
								return;
							}
							frappe.show_alert({
								message: __("Recebimento cancelado. Atos liberados."),
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
		frm.add_custom_button(__("Ver honorários"), function () {
			frappe.set_route("Form", "Fee Agreement", frm.doc.fee_agreement);
		});
	}

	if (["Pendente", "Vencido"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Marcar como Recebido"), function () {
			frappe.confirm(__("Marcar este recebimento como recebido hoje?"), function () {
				frappe.call({
					method: "advocacia.advocacia.painel_api.marcar_parcela_recebida",
					args: { parcela_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Registrando recebimento..."),
					callback: function () {
						frappe.show_alert({
							message: __("Recebimento marcado como recebido."),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
		}).addClass("btn-primary-dark");
	}

	if (["Pendente", "Vencido", "Recebido", "Repassado"].includes(frm.doc.status)) {
		frm.add_custom_button(__("Cancelar Recebimento"), function () {
			const msg_recebido =
				frm.doc.status === "Recebido" || frm.doc.status === "Repassado"
					? __(
							"Cancelar recebimento já recebido? A parcela em honorários voltará para <strong>Cancelado</strong> e o contrato deixará de constar como quitado se aplicável."
					  )
					: __(
							"Cancelar este recebimento? A parcela correspondente em honorários será marcada como <strong>Cancelado</strong>."
					  );

			frappe.confirm(msg_recebido, function () {
				frappe.call({
					method: "advocacia.advocacia.financeiro.cancelar_pagamento_honorarios",
					args: { pagamento_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Cancelando recebimento..."),
					callback: function (r) {
						if (!r.message) {
							return;
						}
						frappe.show_alert({
							message: __("Recebimento cancelado."),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
		}).addClass("btn-danger");
	}
}
