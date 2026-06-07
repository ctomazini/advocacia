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
		if (column.fieldname === "tipo" && row.tipo) {
			const cls = row.tipo === __("Entrada") ? "green" : "red";
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.tipo}</span>`;
		}
		if (column.fieldname === "descricao" && row.descricao && !row.data) {
			return `<strong>${row.descricao}</strong>`;
		}
		if (column.fieldname === "saldo_acumulado" && row.saldo_acumulado != null && !row.data) {
			const cls = flt(row.saldo_acumulado) >= 0 ? "text-success" : "text-danger";
			return `<strong class="${cls}">${value}</strong>`;
		}
		if (
			(column.fieldname === "valor_entrada" || column.fieldname === "valor_saida") &&
			row.descricao &&
			!row.data
		) {
			return `<strong>${value}</strong>`;
		}
		return value;
	},
};
