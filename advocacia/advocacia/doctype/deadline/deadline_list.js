frappe.listview_settings["Deadline"] = {
	...(frappe.listview_settings["Deadline"] || {}),
	hide_name_column: true,
	add_fields: ["status", "due_date", "priority"],
	get_indicator(doc) {
		const hoje = frappe.datetime.get_today();
		const status = doc.status || "Pendente";

		if (status === "Concluído") {
			return [__("Concluído"), "green", "status,=,Concluído"];
		}
		if (status === "Vencido" || (doc.due_date && doc.due_date < hoje && status === "Pendente")) {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.due_date) {
			const diff = frappe.datetime.get_day_diff(doc.due_date, hoje);
			if (diff === 0) {
				return [__("Vence hoje"), "orange", "status,=,Pendente"];
			}
			if (diff > 0 && diff <= 3) {
				return [__("Urgente"), "orange", "status,=,Pendente"];
			}
		}
		if (doc.priority === "Urgente") {
			return [__("Urgente"), "red", "priority,=,Urgente"];
		}
		return [__(status), "blue", "status,=," + status];
	},
};
