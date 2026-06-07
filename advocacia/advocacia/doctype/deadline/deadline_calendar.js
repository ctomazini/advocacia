frappe.views.calendar["Deadline"] = {
	field_map: {
		start: "data_prazo",
		end: "data_prazo",
		id: "name",
		title: "descricao",
		allDay: 1,
		status: "status",
	},
	get_events_method:
		"advocacia.advocacia.doctype.deadline.deadline.get_events",
};
