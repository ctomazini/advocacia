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
			fieldname: "type",
			label: __("Tipo"),
			fieldtype: "Select",
			options: "\nProcesso Judicial\nConsultoria\nAdministrativo\nExtrajudicial",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "situacao_financeira" && row.situacao_financeira) {
			let cls = "green";
			if (row.situacao_financeira.indexOf("Inadimplente") !== -1) {
				cls = "red";
			} else if (row.situacao_financeira.indexOf("Em dia") !== -1) {
				cls = "orange";
			}
			return `<span class="indicator-pill ${cls} filterable ellipsis">${row.situacao_financeira}</span>`;
		}
		if (column.fieldname === "valor_vencido" && flt(row.valor_vencido) > 0) {
			return `<span class="text-danger bold">${value}</span>`;
		}
		if (column.fieldname === "prazo_dias" && row.prazo_dias != null && flt(row.prazo_dias) <= 7) {
			return `<span class="indicator-pill red filterable ellipsis">${value}</span>`;
		}
		return value;
	},
};
