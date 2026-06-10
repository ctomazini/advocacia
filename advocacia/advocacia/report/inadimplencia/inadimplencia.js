frappe.query_reports["inadimplencia"] = {
	filters: [
		{
			fieldname: "client",
			label: __("Cliente"),
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
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "total_vencido" && flt(row.total_vencido) > 0) {
			return `<span class="text-danger bold">${value}</span>`;
		}
		if (column.fieldname === "dias_atraso_max" && flt(row.dias_atraso_max) >= 30) {
			return `<span class="indicator-pill red filterable ellipsis">${value} ${__("dias")}</span>`;
		}
		if (column.fieldname === "dias_atraso_medio" && flt(row.dias_atraso_medio) >= 15) {
			return `<span class="text-danger">${value}</span>`;
		}
		if (column.fieldname === "qtd_parcelas" && flt(row.qtd_parcelas) >= 3) {
			return `<strong>${value}</strong>`;
		}
		return value;
	},
};

advocacia.reports.enhanceReportSettings("inadimplencia");
