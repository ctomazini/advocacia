frappe.query_reports["horas_por_servico"] = {
	filters: [
		{
			fieldname: "servico",
			label: __("Serviço"),
			fieldtype: "Link",
			options: "Servico",
		},
		{
			fieldname: "cliente",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Cliente",
		},
	],
};
