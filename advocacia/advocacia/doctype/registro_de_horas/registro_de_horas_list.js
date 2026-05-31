frappe.listview_settings["Registro de Horas"] = {
	get_indicator(doc) {
		if (doc.timer_ativo) {
			return [__("Timer Ativo"), "red", "timer_ativo,=,1"];
		}
	},
};
