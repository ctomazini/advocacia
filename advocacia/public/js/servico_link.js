(function () {
	if (!frappe.form.link_formatters) {
		return;
	}

	frappe.form.link_formatters.Servico = function (value, doc) {
		if (doc && doc.doctype === "Servico") {
			var parts = [];
			if (doc.title) {
				parts.push(doc.title);
			}
			if (doc.cliente_name) {
				parts.push(doc.cliente_name);
			} else if (doc.cliente && typeof doc.cliente === "string" && doc.cliente !== value) {
				parts.push(doc.cliente);
			}
			if (doc.numero_processo) {
				parts.push(doc.numero_processo);
			}
			if (parts.length) {
				return parts.join(" · ");
			}
		}
		return frappe.utils.get_link_title("Servico", value) || value;
	};
})();
