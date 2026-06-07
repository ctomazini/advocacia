/* eslint-disable */
(function (AP) {
	AP.mostrar_skeleton = function ($container) {
		var html =
			'<div class="painel-skeleton-hero"></div>' +
			'<div class="painel-skeleton-kpis">' +
			'<div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div>' +
			"</div>" +
			'<div class="painel-skeleton-panel"></div><div class="painel-skeleton-panel"></div>';
		$container.html(html);
	};

	AP.handle_error = function ($container, err) {
		var msg = (err && err.message) || String(err);
		$container.html(
			'<div class="painel-panel"><div class="painel-empty" style="color: var(--red-500);">' +
				__("Erro ao carregar o painel: {0}", [msg]) +
				"</div></div>"
		);
	};

	AP._scroll_parent = function (page) {
		var el = page.painel_container[0];
		while (el && el !== document.body) {
			if (el.scrollHeight > el.clientHeight + 1) {
				return $(el);
			}
			el = el.parentElement;
		}
		return $(window);
	};

	AP._save_scroll = function (page) {
		var $sp = AP._scroll_parent(page);
		return { $el: $sp, top: $sp.scrollTop() };
	};

	AP._restore_scroll = function (saved) {
		if (saved && saved.$el) {
			saved.$el.scrollTop(saved.top);
		}
	};

	AP._replace_section = function ($root, selector, html) {
		var $target = $root.find(selector).first();
		if (!$target.length) return false;
		var height = $target.outerHeight();
		if (height > 0) {
			$target.css("min-height", height + "px");
			$target.addClass("painel-section--height-lock");
		}
		$target.replaceWith(html);
		var $next = $root.find(selector).first();
		if ($next.length) {
			requestAnimationFrame(function () {
				requestAnimationFrame(function () {
					$next.css("min-height", "");
					$next.removeClass("painel-section--height-lock");
				});
			});
		}
		return true;
	};

	AP.patch_period_sections = function ($container, d, page) {
		var U = advocacia.painel.utils;
		var F = advocacia.painel.financeiro;
		var periodo = d.periodo_dias || page.painel_periodo || 7;
		page.painel_list_limits = d.list_limits || U.painel_merge_list_limits(page);
		page.painel_data = d;

		$container.find(".painel-periodo-label").text(U.painel_periodo_scope_label(periodo));

		var sections = [
			{ sel: "#painel-hero", key: "hero" },
			{ sel: "#painel-centro-atencao", key: "centro_atencao" },
			{ sel: "#painel-prox-audiencia", key: "prox_audiencia" },
			{ sel: "#painel-saude-operacional", key: "saude_operacional" },
			{ sel: "#painel-timeline", key: "timeline" },
			{ sel: "#painel-comunicacoes", key: "comunicacoes" },
			{ sel: "#painel-indicadores", key: "indicadores" },
			{ sel: "#painel-financeiro", key: "financeiro" },
			{ sel: "#painel-duo-financeiro", key: "duo_financeiro" },
			{ sel: "#painel-duo-secundario", key: "duo_secundario" },
		];

		var missing = false;
		sections.forEach(function (s) {
			var html = AP._period_section_html(s.key, d, page);
			if (!html || !AP._replace_section($container, s.sel, html)) {
				missing = true;
			}
		});

		if (missing) {
			AP.render($container, d, page, { animate: false });
			return;
		}

		F.painel_init_finance_chart($container, d.financeiro, page);
	};

	AP.patch_list_section = function ($container, list_key, d, page) {
		var U = advocacia.painel.utils;
		page.painel_list_limits = d.list_limits || U.painel_merge_list_limits(page);
		page.painel_data = d;

		var html = AP._list_section_html(list_key, d, page);
		if (!html) {
			AP.render($container, d, page, { animate: false });
			return;
		}

		if (!AP._replace_section($container, "#painel-" + list_key, html)) {
			AP.render($container, d, page, { animate: false });
		}
	};
})(advocacia.painel);
