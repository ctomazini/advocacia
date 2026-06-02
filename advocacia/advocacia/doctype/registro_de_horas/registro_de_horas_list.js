frappe.listview_settings["Registro de Horas"] = {
	hide_name_column: true,
	get_indicator(doc) {
		if (doc.timer_ativo) {
			return [__("Timer Ativo"), "red", "timer_ativo,=,1"];
		}
	},
};
