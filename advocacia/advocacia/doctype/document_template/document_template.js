frappe.ui.form.on("Document Template", {
	ver_placeholders(frm) {
		frappe.call({
			method: "advocacia.advocacia.documentos.get_placeholders_referencia",
			freeze: true,
			freeze_message: __("Carregando placeholders..."),
			callback(r) {
				if (!r.message) {
					return;
				}
				render_placeholders_referencia(r.message);
			},
		});
	},
});

function render_placeholders_referencia(blocos) {
	let html = '<div style="max-height:560px;overflow-y:auto;">';

	blocos.forEach((bloco) => {
		const badge = bloco.condicional
			? ' <span class="indicator-pill orange">condicional</span>'
			: "";
		html +=
			'<h5 style="margin-top:14px;margin-bottom:6px;border-bottom:1px solid var(--border-color);padding-bottom:4px;">' +
			frappe.utils.escape_html(bloco.grupo) +
			badge +
			"</h5>";
		html +=
			'<table class="table table-condensed table-bordered" style="font-size:12px;">';
		html += "<thead><tr><th>Placeholder</th><th>Label</th><th>Alias legado</th></tr></thead><tbody>";

		(bloco.items || []).forEach((item) => {
			html +=
				"<tr><td><code>{{ " +
				frappe.utils.escape_html(item.placeholder) +
				" }}</code></td>";
			html += "<td>" + frappe.utils.escape_html(item.label || "") + "</td>";
			html +=
				"<td>" +
				(item.alias
					? "<code>{{ " + frappe.utils.escape_html(item.alias) + " }}</code>"
					: "—") +
				"</td></tr>";
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
}
