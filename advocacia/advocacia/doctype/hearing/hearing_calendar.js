frappe.views.calendar["Hearing"] = {
	field_map: {
		start: "data_hora",
		end: "data_hora",
		id: "name",
		title: "title",
		allDay: 0,
		status: "status_aud",
	},
	get_events_method: "advocacia.advocacia.doctype.hearing.hearing.get_events",
	filters: [
		{
			fieldtype: "Link",
			fieldname: "legal_case",
			options: "Legal Case",
			label: __("Serviço"),
		},
	],
};
