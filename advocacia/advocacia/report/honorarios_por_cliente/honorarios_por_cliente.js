frappe.query_reports["honorarios_por_cliente"] = {
	filters: [
		{
			fieldname: "client",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "de_data",
			label: __("De"),
			fieldtype: "Date",
			default: frappe.datetime.get_today().split("-")[0] + "-01-01",
		},
		{
			fieldname: "ate_data",
			label: __("Até"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "status_filtro",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nPendente\nVencido\nRecebido",
			default: "",
		},
	],
};
