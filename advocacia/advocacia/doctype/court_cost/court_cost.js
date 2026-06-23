frappe.ui.form.on("Court Cost", {
	refresh: function (frm) {
		setup_court_cost_form_intro(frm);
		var status = frm.doc.status;
		if (status === "Pendente") {
			frm.page.set_indicator(__("Pendente"), "red");
		} else if (status === "Pago") {
			frm.page.set_indicator(__("Pago"), "green");
		} else if (status === "Repassado") {
			frm.page.set_indicator(__("Repassado"), "blue");
		} else if (status === "Cancelado") {
			frm.page.set_indicator(__("Cancelado"), "grey");
		}

		if (status === "Pendente" && !frm.is_new()) {
			frm.add_custom_button(__("Marcar como Pago"), function () {
				frm.set_value("payment_date", frappe.datetime.get_today());
				frm.set_value("status", "Pago");
				frm.save();
			}, __("Ações"));
		}

		if (status === "Pago" && frm.doc.bill_to_client && !frm.is_new()) {
			frm.add_custom_button(__("Marcar como Repassado"), function () {
				frm.set_value("transfer_date", frappe.datetime.get_today());
				frm.set_value("status", "Repassado");
				frm.save();
			}, __("Ações"));
		}
	},
});

function setup_court_cost_form_intro(frm) {
	frm.set_intro(
		__(
			"Despesas judiciais vinculadas ao processo: taxas judiciais, custas de perícia, emolumentos, cartório, diligências pagas. Indique quem arca com a despesa (Escritório ou Cliente). Se o cliente reembolsa, registre data e valor."
		),
		"blue"
	);
}
