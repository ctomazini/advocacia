frappe.provide("advocacia");

advocacia.buildPlaceholdersHtml = function (blocos) {
	let html = '<div style="max-height:70vh;overflow-y:auto;">';
	html +=
		'<p class="text-muted small" style="margin-bottom:12px;">' +
		__(
			"Sintaxe docxtpl: <code>{{ placeholder }}</code>. Grupos marcados como <em>condicional</em> só têm valor quando há honorários vinculados ao serviço. A logo usa <code>{{ escritorio_logo }}</code> como imagem inline."
		) +
		"</p>";

	(blocos || []).forEach((bloco) => {
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
		html += "<thead><tr><th>Placeholder</th><th>Descrição</th><th>Alias legado</th></tr></thead><tbody>";

		(bloco.items || []).forEach((item) => {
			const loopVar = item.loop_var ? `${item.loop_var}.` : "";
			const loopBadge = item.loop_only
				? ` <span class="indicator-pill blue">${frappe.utils.escape_html(
						`{% for ${item.loop_var || "item"} in ... %}`
				  )}</span>`
				: "";
			html +=
				"<tr><td><code>{{ " +
				frappe.utils.escape_html(loopVar + item.placeholder) +
				" }}</code>" +
				loopBadge +
				"</td>";
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
	return html;
};

advocacia.showPlaceholdersDialog = function (blocos) {
	const dialog = new frappe.ui.Dialog({
		title: __("Placeholders Disponíveis"),
		size: "extra-large",
		fields: [
			{
				fieldname: "placeholders_html",
				fieldtype: "HTML",
				options: advocacia.buildPlaceholdersHtml(blocos),
			},
		],
		primary_action_label: __("Fechar"),
		primary_action() {
			dialog.hide();
		},
	});
	dialog.show();
};

advocacia.openPlaceholdersReference = function () {
	frappe.call({
		method: "advocacia.advocacia.documentos.get_placeholders_referencia",
		freeze: true,
		freeze_message: __("Carregando placeholders..."),
		callback(r) {
			if (r.exc) {
				frappe.msgprint({
					title: __("Placeholders"),
					indicator: "red",
					message: __("Não foi possível carregar a referência de placeholders."),
				});
				return;
			}
			if (!r.message || !Array.isArray(r.message)) {
				frappe.msgprint({
					title: __("Placeholders"),
					indicator: "orange",
					message: __("Referência de placeholders indisponível."),
				});
				return;
			}
			advocacia.showPlaceholdersDialog(r.message);
		},
	});
};

// Compatibilidade com chamadas legadas
window.advocacia_render_placeholders_referencia = advocacia.showPlaceholdersDialog;
