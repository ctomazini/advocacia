frappe.query_reports["carteira_ativa"] = {
	filters: [
		{
			fieldname: "client",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Client",
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
