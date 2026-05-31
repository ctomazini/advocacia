frappe.provide("advocacia.painel_widget");

(function () {
	var WIDGET_ID = "advocacia-painel-global";
	var HEADER_CLASS = "advocacia-painel-header-btn";
	var started = false;

	function goToPainel() {
		frappe.set_route("painel");
	}

	function isPainelRoute(route) {
		route = route || frappe.get_route() || [];
		if (!route.length) {
			return false;
		}
		if (route[0] === "painel") {
			return true;
		}
		var slug = frappe.router && frappe.router.slug ? frappe.router.slug("painel") : "painel";
		return route[0] === slug;
	}

	function shouldShow() {
		try {
			if (!frappe.session || !frappe.session.user || frappe.session.user === "Guest") {
				return false;
			}
			return !isPainelRoute();
		} catch (e) {
			return false;
		}
	}

	function injectStyles() {
		if (document.getElementById("advocacia-painel-global-styles")) {
			return;
		}
		var style = document.createElement("style");
		style.id = "advocacia-painel-global-styles";
		style.textContent =
			"#advocacia-painel-global {" +
			"position:fixed;" +
			"right:16px;" +
			"bottom:calc(16px + env(safe-area-inset-bottom, 0px));" +
			"display:none;" +
			"align-items:center;" +
			"justify-content:center;" +
			"gap:8px;" +
			"padding:10px 16px;" +
			"border-radius:999px;" +
			"border:none;" +
			"background:var(--primary, #2493ef);" +
			"color:var(--neutral, #fff);" +
			"font-size:13px;" +
			"font-weight:600;" +
			"line-height:1;" +
			"cursor:pointer;" +
			"box-shadow:0 4px 14px rgba(0,0,0,.22);" +
			"z-index:10002;" +
			"max-width:min(240px, calc(100vw - 32px));" +
			"}" +
			"#advocacia-painel-global:hover {" +
			"filter:brightness(1.05);" +
			"}" +
			"#advocacia-painel-global .adv-painel-icon {" +
			"display:inline-flex;align-items:center;" +
			"}" +
			".advocacia-painel-header-btn {" +
			"margin-left:8px;" +
			"}" +
			"@media (max-width:768px) {" +
			"#advocacia-painel-global {" +
			"bottom:calc(72px + env(safe-area-inset-bottom, 0px));" +
			"}" +
			"}";
		document.head.appendChild(style);
	}

	function painelIcon() {
		try {
			return frappe.utils.icon("layout-dashboard", "sm") || "";
		} catch (e) {
			return "◫";
		}
	}

	function ensureFab() {
		injectStyles();
		var el = document.getElementById(WIDGET_ID);
		if (el) {
			return el;
		}

		el = document.createElement("button");
		el.id = WIDGET_ID;
		el.type = "button";
		el.title = __("Ir para o Painel do Escritório");
		el.setAttribute("aria-label", __("Ir para o Painel do Escritório"));
		el.addEventListener("click", goToPainel);
		document.body.appendChild(el);
		return el;
	}

	function syncHeaderButton() {
		if (!shouldShow()) {
			$("." + HEADER_CLASS).remove();
			return;
		}

		var $head = $(".page-container:visible .page-head-content .page-actions").first();
		if (!$head.length) {
			$head = $(".page-head-content:visible .page-actions").first();
		}
		if (!$head.length) {
			return;
		}
		if ($head.find("." + HEADER_CLASS).length) {
			return;
		}

		var $btn = $(
			'<button type="button" class="btn btn-default btn-sm ' +
				HEADER_CLASS +
				'">' +
				frappe.utils.escape_html(__("Painel")) +
				"</button>"
		);
		$btn.on("click", goToPainel);
		$head.prepend($btn);
	}

	function refresh() {
		try {
			var el = ensureFab();
			if (!shouldShow()) {
				el.style.display = "none";
				$("." + HEADER_CLASS).remove();
				return;
			}

			el.style.display = "inline-flex";
			el.innerHTML =
				'<span class="adv-painel-icon">' +
				painelIcon() +
				"</span>" +
				'<span class="adv-painel-label">' +
				frappe.utils.escape_html(__("Painel")) +
				"</span>";

			syncHeaderButton();
		} catch (e) {
			console.error("[advocacia.painel_widget]", e);
		}
	}

	function bindEvents() {
		$(document).on("page-change.advocacia_painel", refresh);
		$(document).on("show.advocacia_painel", ".page-container", refresh);

		if (frappe.router && frappe.router.on) {
			frappe.router.on("change", refresh);
		}

		frappe.after_ajax(function () {
			refresh();
		});
	}

	function start() {
		if (started) {
			refresh();
			return;
		}
		if (!frappe.session || !frappe.session.user || frappe.session.user === "Guest") {
			return;
		}
		started = true;
		bindEvents();
		refresh();
	}

	advocacia.painel_widget = {
		refresh: refresh,
		go: goToPainel,
	};

	$(document).on("app_ready", start);
	$(document).on("startup", start);

	// Fallback caso app_ready já tenha disparado antes deste script.
	setTimeout(start, 0);
	setTimeout(refresh, 500);
	setTimeout(refresh, 1500);
})();
