/* eslint-disable */
frappe.provide("advocacia.painel.atencao");

(function (AP) {
	var U = advocacia.painel.utils;

	function currency_html(value) {
		if (value == null) {
			return "";
		}
		return frappe.format(value, { fieldtype: "Currency" });
	}

	AP.render = function (atencao) {
		atencao = atencao || {};
		var tiles = (atencao.tiles || []).filter(function (tile) {
			return U.cint(tile.count) > 0;
		});

		var bodyHtml;
		if (atencao.all_clear || !tiles.length) {
			bodyHtml =
				'<div class="painel-empty painel-atencao-empty">' +
				U.painel_icon("check-circle") +
				"<span>" +
				frappe.utils.escape_html(atencao.empty_label || __("Nada exige ação agora")) +
				"</span></div>";
		} else {
			var cards = tiles
				.map(function (tile, index) {
					var meta =
						tile.meta != null
							? frappe.utils.escape_html(String(tile.meta))
							: tile.meta_currency != null
								? currency_html(tile.meta_currency)
								: "";
					var pulse = tile.pulse ? " painel-atencao-card--pulse" : "";
					return (
						'<button type="button" class="painel-atencao-card tone-' +
						tile.tone +
						pulse +
						'" data-atencao-index="' +
						index +
						'">' +
						'<div class="painel-atencao-icon">' +
						U.painel_icon(tile.icon || "alert-circle") +
						"</div>" +
						'<div class="painel-atencao-body">' +
						'<div class="painel-atencao-count">' +
						frappe.utils.escape_html(String(tile.count)) +
						"</div>" +
						'<div class="painel-atencao-label">' +
						frappe.utils.escape_html(tile.label || "") +
						"</div>" +
						(meta ? '<div class="painel-atencao-meta">' + meta + "</div>" : "") +
						"</div></button>"
					);
				})
				.join("");
			bodyHtml =
				'<div class="painel-centro-grid">' +
				cards +
				"</div>" +
				'<p class="painel-atencao-ok">' +
				frappe.utils.escape_html(atencao.ok_summary || __("Resto em dia ✓")) +
				"</p>";
		}

		return (
			'<section class="painel-section painel-centro-atencao painel-priority-max" id="painel-centro-atencao" data-atencao-tiles="' +
			frappe.utils.escape_html(JSON.stringify(tiles)) +
			'">' +
			'<div class="painel-section-head">' +
			"<div>" +
			'<h3 class="painel-section-title">' +
			__("Zona de Atenção") +
			"</h3>" +
			'<p class="painel-section-sub">' +
			__("Somente o que exige ação agora") +
			"</p></div></div>" +
			bodyHtml +
			"</section>"
		);
	};

	AP.bind = function ($root, page) {
		$root.on("click.painelAtencaoTiles", ".painel-atencao-card[data-atencao-index]", function () {
			var $section = $(this).closest("#painel-centro-atencao");
			var raw = $section.attr("data-atencao-tiles");
			if (!raw) {
				return;
			}
			var tiles;
			try {
				tiles = JSON.parse(raw);
			} catch (e) {
				return;
			}
			var tile = tiles[U.cint($(this).attr("data-atencao-index"))];
			if (!tile || !tile.deep_link || !tile.deep_link.doctype) {
				return;
			}
			if (typeof advocacia !== "undefined" && advocacia.list_nav && advocacia.list_nav.goto) {
				advocacia.list_nav.goto(tile.deep_link.doctype, tile.deep_link.filters || []);
			}
		});
	};
})(advocacia.painel.atencao);
