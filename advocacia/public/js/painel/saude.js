/* eslint-disable */
frappe.provide("advocacia.painel.saude");

(function (AP) {
	var U = advocacia.painel.utils;

	AP.render = function (saude) {
		saude = saude || {};
		var score = saude.score != null ? saude.score : 0;
		var tone = saude.tone || "green";
		var label = saude.label || __("Saudável");
		var breakdown = saude.breakdown || [];
		var radius = 36;
		var circumference = 2 * Math.PI * radius;
		var offset = circumference - (circumference * score) / 100;

		var rows = breakdown
			.map(function (row) {
				return (
					'<div class="painel-saude-row tone-' +
					(row.tone || "gray") +
					'">' +
					'<span class="painel-saude-row-label">' +
					frappe.utils.escape_html(row.label || "") +
					"</span>" +
					"<strong>" +
					frappe.utils.escape_html(String(row.count)) +
					"</strong></div>"
				);
			})
			.join("");

		return (
			'<div class="painel-saude-card" id="painel-saude-operacional">' +
			'<div class="painel-saude-head">' +
			'<span class="painel-saude-badge tone-' +
			tone +
			'">' +
			U.painel_icon("activity") +
			"</span>" +
			'<h3 class="painel-saude-title">' +
			__("Saúde Operacional") +
			"</h3></div>" +
			'<div class="painel-saude-body">' +
			'<div class="painel-saude-score-wrap">' +
			'<div class="painel-saude-ring">' +
			'<svg viewBox="0 0 88 88" aria-hidden="true">' +
			'<circle class="painel-saude-ring-bg" cx="44" cy="44" r="' +
			radius +
			'"></circle>' +
			'<circle class="painel-saude-ring-fill tone-' +
			tone +
			'" cx="44" cy="44" r="' +
			radius +
			'" stroke-dasharray="' +
			circumference +
			'" stroke-dashoffset="' +
			offset +
			'"></circle></svg>' +
			'<div class="painel-saude-score-text">' +
			'<span class="painel-saude-score-num">' +
			score +
			"%</span>" +
			'<span class="painel-saude-score-label">' +
			frappe.utils.escape_html(label) +
			"</span></div></div>" +
			'<div class="painel-saude-breakdown">' +
			rows +
			"</div></div></div>"
		);
	};
})(advocacia.painel.saude);
