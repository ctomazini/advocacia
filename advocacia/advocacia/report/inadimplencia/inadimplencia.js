frappe.query_reports["inadimplencia"] = {
	filters: [
		{
			fieldname: "cliente",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Cliente",
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
