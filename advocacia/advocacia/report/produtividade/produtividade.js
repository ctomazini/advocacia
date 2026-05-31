frappe.query_reports["produtividade"] = {
	filters: [
		{
			fieldname: "periodo",
			label: __("Período"),
			fieldtype: "Select",
			options: [
				"Último Mês",
				"Últimos 3 Meses",
				"Últimos 6 Meses",
				"Último Ano",
				"Tudo",
			].join("\n"),
			default: "Últimos 6 Meses",
		},
		{
			fieldname: "area",
			label: __("Área Jurídica"),
			fieldtype: "Select",
			options: [
				"",
				"Família",
				"Trabalhista",
				"Cível",
				"Criminal",
				"Previdenciário",
				"Administrativo",
				"Tributário",
			].join("\n"),
		},
		{
			fieldname: "incluir_horas",
			label: __("Incluir Registro de Horas"),
			fieldtype: "Check",
			default: 1,
		},
	],
};
