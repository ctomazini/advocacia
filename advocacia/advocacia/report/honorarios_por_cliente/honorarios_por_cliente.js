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
			label: __("Vencimento desde"),
			fieldtype: "Date",
		},
		{
			fieldname: "ate_data",
			label: __("Vencimento até"),
			fieldtype: "Date",
		},
		{
			fieldname: "status_filtro",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nPendente\nVencido\nRecebido",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (
			["total_contratado", "total_recebido", "pending_total", "total_vencido"].includes(
				column.fieldname
			) &&
			flt(row[column.fieldname]) > 0
		) {
			const danger = column.fieldname === "total_vencido";
			const success = column.fieldname === "total_recebido";
			const cls = danger ? "text-danger bold" : success ? "text-success bold" : "bold";
			return `<span class="${cls}">${value}</span>`;
		}
		if (column.fieldname === "pct_recebido" && row.pct_recebido != null) {
			const pct = flt(row.pct_recebido);
			const cls = pct >= 80 ? "text-success" : pct >= 50 ? "text-warning" : "text-danger";
			return `<span class="${cls} bold">${value}</span>`;
		}
		return value;
	},
};

advocacia.reports.enhanceReportSettings("honorarios_por_cliente");
