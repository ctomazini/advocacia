frappe.query_reports["produtividade"] = {
	filters: [
		{
			fieldname: "periodo",
			label: __("Período"),
			fieldtype: "Select",
			options: [
				"Último Mês",
				"Últimos 3 Meses",
				"Últimos 6 Meses",
				"Último Ano",
				"Tudo",
			].join("\n"),
			default: "Últimos 6 Meses",
		},
		{
			fieldname: "area",
			label: __("Área Jurídica"),
			fieldtype: "Select",
			options: [
				"",
				"Família",
				"Trabalhista",
				"Cível",
				"Criminal",
				"Previdenciário",
				"Administrativo",
				"Tributário",
			].join("\n"),
		},
		{
			fieldname: "incluir_horas",
			label: __("Incluir Time Entry"),
			fieldtype: "Check",
			default: 1,
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (row.area === __("Total")) {
			if (
				[
					"total_servicos",
					"total_honorarios",
					"total_custas",
					"lucro_liquido",
					"horas_registradas",
				].includes(column.fieldname)
			) {
				const cls =
					column.fieldname === "lucro_liquido" && flt(row.lucro_liquido) < 0
						? "text-danger bold"
						: "bold";
				return `<strong class="${cls}">${value}</strong>`;
			}
		}
		if (column.fieldname === "lucro_liquido" && flt(row.lucro_liquido) < 0) {
			return `<span class="text-danger">${value}</span>`;
		}
		if (column.fieldname === "taxa_encerramento" && flt(row.taxa_encerramento) >= 50) {
			return `<span class="text-success bold">${value}</span>`;
		}
		return value;
	},
};

advocacia.reports.enhanceReportSettings("produtividade");
