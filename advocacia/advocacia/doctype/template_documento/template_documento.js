frappe.ui.form.on("Template Documento", {
	ver_placeholders: function (frm) {
		frappe.call({
			method: "advocacia.advocacia.documentos.get_placeholders_disponiveis",
			freeze: true,
			freeze_message: __("Carregando placeholders..."),
			callback: function (r) {
				if (!r.message) {
					return;
				}

				var grupos = r.message;
				var html = '<div style="max-height:500px;overflow-y:auto;">';

				var ordem = [
					"Aliases Legados",
					"Data",
					"Servico",
					"Cliente",
					"Endereco Cliente",
					"Contato Cliente",
					"Acordo de Honorarios Processuais",
				];

				ordem.forEach(function (grupo) {
					if (!grupos[grupo]) {
						return;
					}
					var campos = grupos[grupo];
					html +=
						'<h5 style="margin-top:12px;margin-bottom:4px;border-bottom:1px solid #d1d8dd;padding-bottom:4px;">' +
						frappe.utils.escape_html(grupo) +
						"</h5>";
					html +=
						'<table class="table table-condensed table-bordered" style="font-size:12px;">';
					html +=
						"<thead><tr><th>Placeholder</th><th>Label</th><th>Tipo</th></tr></thead><tbody>";
					campos.forEach(function (c) {
						html +=
							"<tr><td><code>{{ " +
							frappe.utils.escape_html(c.placeholder) +
							" }}</code></td>";
						html +=
							"<td>" + frappe.utils.escape_html(c.label) + "</td>";
						html +=
							"<td>" + frappe.utils.escape_html(c.fieldtype) + "</td></tr>";
					});
					html += "</tbody></table>";
				});

				html += "</div>";

				frappe.msgprint({
					title: __("Placeholders Disponíveis"),
					message: html,
					wide: true,
					indicator: "blue",
				});
			},
		});
	},
});
