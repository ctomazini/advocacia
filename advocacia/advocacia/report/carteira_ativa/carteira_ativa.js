frappe.query_reports["Carteira Ativa"] = {
	filters: [
		{
			fieldname: "cliente",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Cliente",
		},
		{
			fieldname: "area",
			label: __("Área"),
			fieldtype: "Select",
			options:
				"\nFamília\nTrabalhista\nCível\nPrevidenciário\nConsumidor\nTributário\nPenal\nAdministrativo",
		},
		{
			fieldname: "tipo",
			label: __("Tipo"),
			fieldtype: "Select",
			options: "\nProcesso Judicial\nConsultoria\nAdministrativo\nExtrajudicial",
		},
	],
};
