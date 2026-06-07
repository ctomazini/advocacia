frappe.pages.painel = frappe.pages.painel || {};

const PAINEL_ASSETS = [
	"/assets/advocacia/js/painel/utils.js",
	"/assets/advocacia/js/painel/hero.js",
	"/assets/advocacia/js/painel/kpis.js",
	"/assets/advocacia/js/painel/audiencias.js",
	"/assets/advocacia/js/painel/timeline.js",
	"/assets/advocacia/js/painel/financeiro.js",
	"/assets/advocacia/js/painel/refresh.js",
	"/assets/advocacia/js/painel/sections.js",
	"/assets/advocacia/js/painel/handlers.js",
	"/assets/advocacia/js/painel/index.js",
];

frappe.pages.painel.on_page_load = function (wrapper) {
	frappe.require(PAINEL_ASSETS, function () {
		if (typeof advocacia !== "undefined" && advocacia.painel && advocacia.painel.init) {
			advocacia.painel.init(wrapper);
		} else {
			frappe.msgprint(__("Módulos do painel não carregados. Execute bench build --app advocacia."));
		}
	});
};

frappe.pages.painel.on_page_hide = function () {
	$(document.body).removeClass("advocacia-painel-active");
};
