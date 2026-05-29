frappe.query_reports["Fluxo de Caixa Projetado"] = {
	filters: [
		{
			fieldname: "meses",
			label: __("Horizonte (meses)"),
			fieldtype: "Select",
			options: "3\n6\n12",
			default: "6",
		},
		{
			fieldname: "cliente",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Cliente",
		},
		{
			fieldname: "incluir_vencidos",
			label: __("Incluir vencidos acumulados"),
			fieldtype: "Check",
			default: 1,
		},
	],
};
