var COMUNICACAO_TIPO_COLORS = {
	Telefone: "blue",
	WhatsApp: "green",
	Email: "orange",
	"Reunião Presencial": "purple",
	"Reunião Virtual": "cyan",
	Outro: "grey",
};

frappe.ui.form.on("Case Communication", {
	refresh: function (frm) {
		var color = COMUNICACAO_TIPO_COLORS[frm.doc.type] || "grey";
		if (frm.doc.type) {
			frm.page.set_indicator(frm.doc.type, color);
		}

		if (frm.doc.legal_case && !frm.is_new()) {
			frm.add_custom_button(__("Ver Serviço"), function () {
				frappe.set_route("Form", "Legal Case", frm.doc.legal_case);
			});
		}
	},
});
