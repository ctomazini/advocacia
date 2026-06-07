frappe.query_reports["inadimplencia"] = {
	filters: [
		{
			fieldname: "client",
			label: __("Client"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "de_data",
			label: __("Vencimento desde"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "ate_data",
			label: __("Vencimento até"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
