frappe.provide("advocacia.timer_global");

(function () {
	var WIDGET_ID = "advocacia-timer-global";
	var SYNC_MS = 45000;
	var API = "advocacia.advocacia.doctype.registro_de_horas.registro_de_horas.get_timer_ativo_usuario";

	var state = null;
	var tickInterval = null;
	var syncInterval = null;
	var syncing = false;

	function pad(n) {
		return String(n).padStart(2, "0");
	}

	function formatElapsed(startStr) {
		if (!startStr) return "00:00:00";
		var start = frappe.datetime.str_to_obj(startStr);
		var diff = Math.floor((new Date() - start) / 1000);
		if (diff < 0) diff = 0;
		var h = Math.floor(diff / 3600);
		var m = Math.floor((diff % 3600) / 60);
		var s = diff % 60;
		return pad(h) + ":" + pad(m) + ":" + pad(s);
	}

	function timerIcon() {
		try {
			return frappe.utils.icon("clock", "sm") || "";
		} catch (e) {
			return "⏱";
		}
	}

	function injectStyles() {
		if (document.getElementById("advocacia-timer-global-styles")) return;
		var style = document.createElement("style");
		style.id = "advocacia-timer-global-styles";
		style.textContent =
			"#advocacia-timer-global {" +
			"position:fixed;" +
			"left:16px;" +
			"bottom:calc(16px + env(safe-area-inset-bottom, 0px));" +
			"display:none;" +
			"align-items:center;" +
			"gap:8px;" +
			"padding:10px 14px;" +
			"border-radius:999px;" +
			"border:1px solid color-mix(in srgb, var(--red-500) 35%, var(--border-color));" +
			"background:color-mix(in srgb, var(--red-500) 12%, var(--card-bg));" +
			"color:var(--text-color);" +
			"font-size:13px;" +
			"font-weight:600;" +
			"cursor:pointer;" +
			"box-shadow:var(--shadow-md, 0 4px 12px rgba(0,0,0,.15));" +
			"z-index:9998;" +
			"max-width:min(320px, calc(100vw - 32px));" +
			"transition:transform .18s ease, box-shadow .18s ease;" +
			"}" +
			"#advocacia-timer-global:hover {" +
			"transform:translateY(-1px);" +
			"box-shadow:var(--shadow-lg, 0 6px 16px rgba(0,0,0,.2));" +
			"}" +
			"#advocacia-timer-global .adv-timer-dot {" +
			"width:8px;height:8px;border-radius:50%;flex-shrink:0;" +
			"background:var(--red-500);" +
			"animation:adv-timer-pulse 1.5s ease-in-out infinite;" +
			"}" +
			"#advocacia-timer-global .adv-timer-clock {" +
			"font-family:var(--font-stack-monospace, 'Courier New', monospace);" +
			"font-variant-numeric:tabular-nums;" +
			"}" +
			"#advocacia-timer-global .adv-timer-label {" +
			"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" +
			"color:var(--text-muted);font-weight:500;" +
			"}" +
			"@keyframes adv-timer-pulse {" +
			"0%,100%{opacity:1}50%{opacity:.35}" +
			"}";
		document.head.appendChild(style);
	}

	function ensureWidget() {
		injectStyles();
		var el = document.getElementById(WIDGET_ID);
		if (el) return el;

		el = document.createElement("button");
		el.id = WIDGET_ID;
		el.type = "button";
		el.title = __("Timer em execução — clique para abrir o registro");
		el.onclick = function () {
			if (state && state.name) {
				frappe.set_route("Form", "Registro de Horas", state.name);
			}
		};
		document.body.appendChild(el);
		return el;
	}

	function renderWidget() {
		var el = ensureWidget();
		if (!state || !state.timer_inicio) {
			el.style.display = "none";
			return;
		}

		el.style.display = "inline-flex";
		var clock = formatElapsed(state.timer_inicio);
		var label = frappe.utils.escape_html(state.atividade || state.name || "");
		el.innerHTML =
			'<span class="adv-timer-dot"></span>' +
			'<span class="adv-timer-icon">' +
			timerIcon() +
			"</span>" +
			'<span class="adv-timer-clock">' +
			clock +
			"</span>" +
			(label ? '<span class="adv-timer-label">' + label + "</span>" : "");
	}

	function startTicking() {
		if (tickInterval) return;
		tickInterval = setInterval(renderWidget, 1000);
	}

	function stopTicking() {
		if (tickInterval) {
			clearInterval(tickInterval);
			tickInterval = null;
		}
	}

	function applyState(data) {
		if (data && data.name && data.timer_inicio) {
			state = data;
			startTicking();
		} else {
			state = null;
			stopTicking();
		}
		renderWidget();
	}

	function syncFromServer() {
		if (frappe.session.user === "Guest" || syncing) return;
		syncing = true;
		frappe
			.xcall(API)
			.then(function (data) {
				applyState(data);
			})
			.finally(function () {
				syncing = false;
			});
	}

	function ensureSyncLoop() {
		if (syncInterval) return;
		syncFromServer();
		syncInterval = setInterval(syncFromServer, SYNC_MS);
	}

	advocacia.timer_global = {
		refresh: syncFromServer,
	};

	frappe.after_ajax(function () {
		if (frappe.session.user !== "Guest") {
			ensureSyncLoop();
		}
	});

	$(document).on("page-change", function () {
		if (frappe.session.user !== "Guest" && !state) {
			syncFromServer();
		}
	});
})();
