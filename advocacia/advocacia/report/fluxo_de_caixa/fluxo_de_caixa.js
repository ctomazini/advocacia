frappe.query_reports["fluxo_de_caixa"] = {
	filters: [
		{
			fieldname: "meses",
			label: __("Horizonte (meses)"),
			fieldtype: "Select",
			options: "3\n6\n12",
			default: "6",
		},
		{
			fieldname: "client",
			label: __("Client"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "incluir_despesas",
			label: __("Incluir despesas do escritório"),
			fieldtype: "Check",
			default: 1,
		},
	],
};
