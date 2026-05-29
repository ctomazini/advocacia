frappe.ui.form.on("Pagamento", {
	refresh(frm) {
		if (frm.doc.status === "Cancelado" && !frm.is_new()) {
			frm.set_read_only();
			frm.set_intro(
				__(
					"Pagamento cancelado — registro imutável. Nova parcela no honorário gera um novo pagamento."
				),
				"blue"
			);
		}
	},
});
