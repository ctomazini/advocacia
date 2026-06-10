frappe.listview_settings["Hearing"] = {
	hide_name_column: true,
	get_indicator(doc) {
		const status = doc.status || "Agendada";
		const colors = {
			Agendada: "blue",
			Realizada: "green",
			Adiada: "orange",
			Cancelada: "red",
		};
		return [__(status), colors[status] || "gray", "status_aud,=," + status];
	},
};
