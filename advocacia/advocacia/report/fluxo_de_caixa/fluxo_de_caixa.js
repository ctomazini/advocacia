frappe.query_reports["fluxo_de_caixa"] = {
	filters: [
		{
			fieldname: "meses",
			label: __("Horizonte (meses)"),
			fieldtype: "Select",
			options: "3\n6\n12",
			default: "6",
		},
		{
			fieldname: "client",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "incluir_despesas",
			label: __("Incluir despesas do escritório"),
			fieldtype: "Check",
			default: 1,
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "type" && row.type) {
			const cls = row.type === __("Entrada") ? "green" : "red";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.type}</span>`;
		}
		if (column.fieldname === "description" && row.description && !row.date) {
			return `<strong>${row.description}</strong>`;
		}
		if (column.fieldname === "saldo_acumulado" && row.saldo_acumulado != null && !row.date) {
			const cls = flt(row.saldo_acumulado) >= 0 ? "text-success" : "text-danger";
			return `<strong class="${cls}">${value}</strong>`;
		}
		if (
			(column.fieldname === "valor_entrada" || column.fieldname === "valor_saida") &&
			row.description &&
			!row.date
		) {
			return `<strong>${value}</strong>`;
		}
		return value;
	},
};
