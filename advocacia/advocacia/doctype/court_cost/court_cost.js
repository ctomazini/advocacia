frappe.ui.form.on("Court Cost", {
	refresh: function (frm) {
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
