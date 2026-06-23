frappe.listview_settings["Hearing"] = {
	...(frappe.listview_settings["Hearing"] || {}),
	hide_name_column: true,
	add_fields: ["status", "hearing_datetime"],
	get_indicator(doc) {
		const status = doc.status || "Agendada";
		const colors = {
			Agendada: "blue",
			Realizada: "green",
			Adiada: "orange",
			Cancelada: "red",
		};

		if (status === "Realizada" || status === "Cancelada") {
			return [__(status), colors[status] || "gray", "status,=," + status];
		}

		if (doc.hearing_datetime) {
			const hoje = frappe.datetime.get_today();
			const hearingDate = frappe.datetime.obj_to_str(
				frappe.datetime.str_to_obj(doc.hearing_datetime)
			).split(" ")[0];
			const diff = frappe.datetime.get_day_diff(hearingDate, hoje);
			if (diff < 0) {
				return [__("Passada"), "red", "status,=," + status];
			}
			if (diff === 0) {
				return [__("Hoje"), "orange", "status,=," + status];
			}
		}

		return [__(status), colors[status] || "gray", "status,=," + status];
	},
};
