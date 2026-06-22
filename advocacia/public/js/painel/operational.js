/* eslint-disable */
frappe.provide("advocacia.painel.operational");

(function (AP) {
	var U = advocacia.painel.utils;

	AP.render = function (active_cases, list_meta, list_limit) {
		list_meta = list_meta || {};
		list_limit = list_limit != null ? U.cint(list_limit) : 5;
		active_cases = active_cases || [];
		var meta_html = U.painel_list_meta_html(list_meta, list_limit);

		var rows = active_cases
			.map(function (row) {
				var nextHtml = "";
				if (row.next_event_label) {
					var dateStr = row.next_event_date
						? frappe.datetime.str_to_user(row.next_event_date)
						: "";
					var overdueCls = row.next_event_overdue ? " danger" : " text-muted";
					nextHtml =
						'<div class="painel-op-sub' +
						overdueCls +
						'">' +
						frappe.utils.escape_html(dateStr) +
						(row.next_event_label
							? " · " + frappe.utils.escape_html(row.next_event_label)
							: "") +
						"</div>";
				}
				var subParts = [row.client_name, row.case_phase, row.type].filter(Boolean);
				return (
					'<button type="button" class="painel-op-row" data-dt="Legal Case" data-dn="' +
					frappe.utils.escape_html(row.name) +
					'">' +
					"<div>" +
					'<div class="painel-op-row__title">' +
					frappe.utils.escape_html(row.title || row.name) +
					"</div>" +
					'<div class="painel-op-row__sub">' +
					frappe.utils.escape_html(subParts.join(" · ")) +
					"</div>" +
					nextHtml +
					"</div>" +
					'<div class="painel-op-side">' +
					'<span class="indicator-pill blue filterable no-indicator-dot ellipsis">' +
					frappe.utils.escape_html(row.status || "") +
					"</span></div></button>"
				);
			})
			.join("");

		var body = rows
			? '<div class="painel-op-list">' + rows + "</div>"
			: U.render_empty_state(
					"briefcase",
					__("Nenhum processo ativo"),
					__("Processos em andamento aparecerão aqui.")
			  );

		return (
			'<section class="painel-section painel-priority-medium" id="painel-active_cases">' +
			'<div class="painel-section-head">' +
			"<div><h2 class='painel-section-title'>" +
			__("Processos Ativos") +
			"</h2>" +
			'<p class="painel-section-sub">' +
			__("Carteira em andamento") +
			"</p></div>" +
			'<div class="painel-section-head-actions">' +
			U.render_list_limit_controls("active_cases", list_limit) +
			meta_html +
			'<span class="painel-section-link" data-route-list="Legal Case">' +
			__("Ver todos") +
			"</span></div></div>" +
			'<div class="painel-panel">' +
			body +
			"</div></section>"
		);
	};
})(advocacia.painel.operational);
