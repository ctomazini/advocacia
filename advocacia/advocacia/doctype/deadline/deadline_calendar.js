frappe.views.calendar["Deadline"] = {
	field_map: {
		start: "due_date",
		end: "due_date",
		id: "name",
		title: "description",
		allDay: 1,
		status: "status",
	},
	get_events_method:
		"advocacia.advocacia.doctype.deadline.deadline.get_events",
};
