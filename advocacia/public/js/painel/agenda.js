/* eslint-disable */
frappe.provide("advocacia.painel.agenda");

(function (AP) {
	var U = advocacia.painel.utils;

	function type_label(tipo) {
		if (tipo === "audiencia") {
			return __("Audiência");
		}
		if (tipo === "prazo") {
			return __("Prazo");
		}
		if (tipo === "legal_task") {
			return __("Tarefa");
		}
		return __("Compromisso");
	}

	AP.render_day_strip = function (agenda_dias) {
		agenda_dias = agenda_dias || [];
		if (!agenda_dias.length) {
			return "";
		}
		var days = agenda_dias
			.map(function (day) {
				return (
					'<div class="painel-agenda-day tone-' +
					(day.tone || "gray") +
					'">' +
					'<span class="painel-agenda-day-label">' +
					frappe.utils.escape_html(day.label || "") +
					"</span>" +
					'<span class="painel-agenda-day-count">' +
					frappe.utils.escape_html(String(day.count || 0)) +
					"</span></div>"
				);
			})
			.join("");
		return (
			'<div class="painel-agenda-strip" id="painel-agenda-dias">' +
			days +
			"</div>"
		);
	};

	AP.render_proximo_evento = function (proximo_evento) {
		proximo_evento = proximo_evento || [];
		var bodyHtml;
		if (!proximo_evento.length) {
			bodyHtml =
				'<div class="painel-empty">' +
				U.painel_icon("check-circle") +
				"<span>" +
				__("Nenhum compromisso pendente ✓") +
				"</span></div>";
		} else {
			bodyHtml =
				'<div class="painel-centro-grid">' +
				proximo_evento
					.map(function (item) {
						var headline = item.hora || item.when_label || "—";
						var meta = [item.title || "", item.subtitle || ""]
							.filter(Boolean)
							.join(" · ");
						return (
							'<button type="button" class="painel-atencao-card painel-compromisso-card tone-' +
							(item.urgencia || "gray") +
							'" data-doctype="' +
							frappe.utils.escape_html(item.doctype || "") +
							'" data-name="' +
							frappe.utils.escape_html(item.docname || "") +
							'">' +
							'<div class="painel-atencao-icon">' +
							U.painel_icon(item.icon || "calendar") +
							"</div>" +
							'<div class="painel-atencao-body">' +
							'<div class="painel-atencao-count">' +
							frappe.utils.escape_html(headline) +
							"</div>" +
							'<div class="painel-atencao-label">' +
							frappe.utils.escape_html(type_label(item.type || item.type)) +
							"</div>" +
							(meta
								? '<div class="painel-atencao-meta">' +
									frappe.utils.escape_html(meta) +
									"</div>"
								: "") +
							"</div></button>"
						);
					})
					.join("") +
				"</div>";
		}

		return (
			'<section class="painel-agenda-proximo painel-dashboard-card" id="painel-proximo-evento">' +
			'<div class="painel-section-head">' +
			"<div>" +
			'<h3 class="painel-section-title">' +
			__("Próximos compromissos") +
			"</h3>" +
			'<p class="painel-section-sub">' +
			__("Os dois mais urgentes na agenda") +
			"</p></div></div>" +
			bodyHtml +
			"</section>"
		);
	};

	AP.render = function (agenda_dias, proximo_evento) {
		return AP.render_day_strip(agenda_dias) + AP.render_proximo_evento(proximo_evento);
	};

	AP.bind = function ($root) {
		$root.on(
			"click.painelProximoEvento",
			".painel-compromisso-card[data-doctype][data-name]",
			function () {
				var doctype = $(this).attr("data-doctype");
				var name = $(this).attr("data-name");
				if (doctype && name) {
					frappe.set_route("Form", doctype, name);
				}
			}
		);
	};
})(advocacia.painel.agenda);
