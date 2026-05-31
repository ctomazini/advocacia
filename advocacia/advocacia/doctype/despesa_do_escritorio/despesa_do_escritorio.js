frappe.ui.form.on("Despesa do Escritorio", {
	refresh: function (frm) {
		if (frm.doc.status === "Atrasado") {
			frm.dashboard.set_headline(
				__('<span style="color:var(--red-500)">⚠ Despesa atrasada!</span>')
			);
		}
		if (frm.doc.status === "Pago") {
			frm.page.set_indicator(__("Pago"), "green");
		}

		if (frm.doc.recorrente && !frm.is_new() && frm.doc.proximo_vencimento) {
			frm.add_custom_button(__("Gerar Próxima"), function () {
				frappe.call({
					method:
						"advocacia.advocacia.doctype.despesa_do_escritorio.despesa_do_escritorio.gerar_proxima_despesa",
					args: { source_name: frm.doc.name },
					callback: function (r) {
						if (r.message) {
							frappe.set_route("Form", "Despesa do Escritorio", r.message);
						}
					},
				});
			}, __("Ações"));
		}
	},

	data_pagamento: function (frm) {
		if (frm.doc.data_pagamento) {
			frm.set_value("status", "Pago");
		}
	},
});
