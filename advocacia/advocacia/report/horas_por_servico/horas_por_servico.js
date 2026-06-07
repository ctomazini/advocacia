frappe.query_reports["horas_por_servico"] = {
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
				"Personalizado",
			].join("\n"),
			default: "Últimos 6 Meses",
		},
		{
			fieldname: "de_data",
			label: __("De"),
			fieldtype: "Date",
			depends_on: 'eval:doc.periodo=="Personalizado"',
		},
		{
			fieldname: "ate_data",
			label: __("Até"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			depends_on: 'eval:doc.periodo=="Personalizado"',
		},
		{
			fieldname: "client",
			label: __("Cliente"),
			fieldtype: "Link",
			options: "Client",
		},
		{
			fieldname: "legal_case",
			label: __("Serviço"),
			fieldtype: "Link",
			options: "Legal Case",
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
				"Consumidor",
				"Penal",
			].join("\n"),
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "horas_cobraveis" && flt(row.horas_cobraveis) > 0) {
			return `<span class="text-success bold">${value}</span>`;
		}
		if (column.fieldname === "horas_nao_cobraveis" && flt(row.horas_nao_cobraveis) > 0) {
			return `<span class="text-muted">${value}</span>`;
		}
		if (column.fieldname === "pct_cobravel" && row.pct_cobravel != null) {
			const pct = flt(row.pct_cobravel);
			const cls = pct >= 70 ? "text-success" : pct >= 40 ? "text-warning" : "text-danger";
			return `<span class="${cls} bold">${value}</span>`;
		}
		if (column.fieldname === "total_horas" && !row.legal_case) {
			return `<strong>${value}</strong>`;
		}
		return value;
	},
};
