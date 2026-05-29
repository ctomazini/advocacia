frappe.views.calendar["Audiencia"] = {
	field_map: {
		start: "data_hora",
		end: "data_hora",
		id: "name",
		title: "title",
		allDay: 0,
		status: "status_aud",
	},
	get_events_method: "advocacia.advocacia.doctype.audiencia.audiencia.get_events",
	filters: [
		{
			fieldtype: "Link",
			fieldname: "servico",
			options: "Servico",
			label: __("Serviço"),
		},
	],
};
