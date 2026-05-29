frappe.listview_settings["Pagamento"] = {
	add_fields: ["status", "data_vencimento", "cliente", "servico", "valor"],
	get_indicator(doc) {
		if (doc.status === "Vencido") {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.status === "Recebido" || doc.status === "Repassado") {
			return [__(doc.status), "green", "status,=," + doc.status];
		}
		if (doc.status === "Pendente" && doc.data_vencimento) {
			const hoje = frappe.datetime.get_today();
			const diff = frappe.datetime.get_day_diff(doc.data_vencimento, hoje);
			if (diff >= 0 && diff <= 7) {
				return [__("Próximo vencimento"), "orange", "status,=,Pendente"];
			}
		}
		if (doc.status === "Cancelado") {
			return [__("Cancelado"), "gray", "status,=,Cancelado"];
		}
		return [__(doc.status || "Pendente"), "blue", "status,=," + (doc.status || "Pendente")];
	},
	onload(listview) {
		const hoje = frappe.datetime.get_today();
		const sete = frappe.datetime.add_days(hoje, 7);

		listview.page.add_inner_button(__("Vencidos"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([[listview.doctype, "status", "=", "Vencido"]]);
		});

		listview.page.add_inner_button(__("Próximos 7 dias"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([
				[listview.doctype, "status", "=", "Pendente"],
				[listview.doctype, "data_vencimento", "between", [hoje, sete]],
			]);
		});

		listview.page.add_inner_button(__("Recebidos hoje"), () => {
			listview.filter_area.clear();
			listview.filter_area.add([
				[listview.doctype, "status", "in", ["Recebido", "Repassado"]],
				[listview.doctype, "data_recebimento", "=", hoje],
			]);
		});
	},
};
