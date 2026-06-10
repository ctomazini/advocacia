frappe.ui.form.on("Hearing", {
	refresh(frm) {
		if (frm.doc.modality === "Virtual" || frm.doc.modality === "Híbrida") {
			frm.add_custom_button(__("🖥️ Entrar na Audiência"), function () {
				if (frm.doc.link_virtual) {
					window.open(frm.doc.link_virtual, "_blank");
					return;
				}
				frappe.msgprint({
					title: __("Link não cadastrado"),
					message: __(
						"Esta audiência virtual ainda não possui link. Cadastre o link no campo acima quando estiver disponível."
					),
					indicator: "orange",
				});
			}).addClass("btn-primary");
		}
	},
	modalidade(frm) {
		if (frm.doc.modality === "Presencial") {
			frm.set_value("link_virtual", "");
		}
	},
});
