frappe.query_reports["horas_por_servico"] = {
	filters: [
		{
			fieldname: "legal_case",
			label: __("Serviço"),
			fieldtype: "Link",
			options: "Legal Case",
		},
		{
			fieldname: "client",
			label: __("Client"),
			fieldtype: "Link",
			options: "Client",
		},
	],
};
