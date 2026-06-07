frappe.listview_settings["Client"] = {
	hide_name_column: true,
	formatters: {
		tipo_pessoa(value, _df, doc) {
			const tipo = frappe.utils.escape_html(value || "");
			const id = frappe.utils.escape_html(doc.name || "");
			const badge = id
				? `<span class="indicator-pill gray ellipsis" style="max-width: 130px; margin-right: 6px;">${id}</span>`
				: "";

			return `${badge}<span>${tipo}</span>`;
		},
	},
};
