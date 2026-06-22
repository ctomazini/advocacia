frappe.views.calendar["Hearing"] = {
	field_map: {
		start: "hearing_datetime",
		end: "hearing_datetime",
		id: "name",
		title: "title",
		allDay: 0,
		status: "status",
	},
	get_events_method: "advocacia.advocacia.doctype.hearing.hearing.get_events",
	filters: [
		{
			fieldtype: "Link",
			fieldname: "legal_case",
			options: "Legal Case",
			label: __("Processo"),
		},
	],
};
