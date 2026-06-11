frappe.ui.form.on("Case Document", {
	setup(frm) {
		frm.set_query("related_deadline", () => ({
			filters: {
				legal_case: frm.doc.legal_case,
			},
		}));
	},

	legal_case(frm) {
		if (frm.doc.related_deadline) {
			frm.set_value("related_deadline", "");
		}
	},
});
