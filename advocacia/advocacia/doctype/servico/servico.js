frappe.ui.form.on("Servico", {
	refresh: function (frm) {
		aplicar_mascara_processo_servico(frm);

		if (frm.is_new()) return;

		frm.add_custom_button("+ Honorários", function () {
			frappe.new_doc("Acordo de Honorarios Processuais", {
				servico: frm.doc.name,
				cliente: frm.doc.cliente,
			});
		}, "Criar");

		frm.add_custom_button("+ Prazo", function () {
			frappe.new_doc("Controle de Prazos", {
				servico: frm.doc.name,
			});
		}, "Criar");

		frm.add_custom_button("+ Audiência", function () {
			frappe.new_doc("Audiencia", {
				servico: frm.doc.name,
			});
		}, "Criar");
	},
	tipo: function (frm) {
		aplicar_mascara_processo_servico(frm);
	},
	numeracao_legada: function (frm) {
		aplicar_mascara_processo_servico(frm);
	},
});

function aplicar_mascara_processo_servico(frm) {
	var field = frm.fields_dict.numero_processo;
	if (!field || !field.$input) return;

	field.$input.off(".advocacia_mask");
	if ($.fn.inputmask && field.$input.inputmask) {
		field.$input.inputmask("remove");
	}

	if (frm.doc.tipo !== "Processo Judicial" || frm.doc.numeracao_legada) {
		return;
	}

	if (typeof advocacia_aplicar_mascara_input === "function") {
		advocacia_aplicar_mascara_input(field.$input, "cnj");
		return;
	}

	if ($.fn.inputmask) {
		field.$input.inputmask("9999999-99.9999.9.99.9999");
	}
}
