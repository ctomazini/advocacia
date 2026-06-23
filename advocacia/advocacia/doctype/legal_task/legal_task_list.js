frappe.listview_settings["Legal Task"] = {
	...(frappe.listview_settings["Legal Task"] || {}),
	hide_name_column: true,
	add_fields: ["status", "priority", "due_date"],
	get_indicator(doc) {
		const status = doc.status || "Pendente";
		const colors = {
			Pendente: "orange",
			"Em Andamento": "blue",
			Concluída: "green",
			Cancelada: "gray",
		};
		if (status === "Concluída" || status === "Cancelada") {
			return [__(status), colors[status] || "gray", "status,=," + status];
		}
		const hoje = frappe.datetime.get_today();
		if (doc.due_date && doc.due_date < hoje) {
			return [__("Atrasada"), "red", "status,=," + status];
		}
		if (doc.priority === "Alta") {
			return [__("Prioridade alta"), "red", "priority,=,Alta"];
		}
		return [__(status), colors[status] || "blue", "status,=," + status];
	},
};
