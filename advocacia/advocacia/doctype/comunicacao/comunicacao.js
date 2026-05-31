var COMUNICACAO_TIPO_COLORS = {
	Telefone: "blue",
	WhatsApp: "green",
	Email: "orange",
	"Reunião Presencial": "purple",
	"Reunião Virtual": "cyan",
	Outro: "grey",
};

frappe.ui.form.on("Comunicacao", {
	refresh: function (frm) {
		var color = COMUNICACAO_TIPO_COLORS[frm.doc.tipo] || "grey";
		if (frm.doc.tipo) {
			frm.page.set_indicator(frm.doc.tipo, color);
		}

		if (frm.doc.servico && !frm.is_new()) {
			frm.add_custom_button(__("Ver Serviço"), function () {
				frappe.set_route("Form", "Servico", frm.doc.servico);
			});
		}
	},
});
