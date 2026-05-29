frappe.views.calendar["Controle de Prazos"] = {
	field_map: {
		start: "data_prazo",
		end: "data_prazo",
		id: "name",
		title: "descricao",
		allDay: 1,
		status: "status",
	},
	get_events_method:
		"advocacia.advocacia.doctype.controle_de_prazos.controle_de_prazos.get_events",
};
