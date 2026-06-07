frappe.pages.painel = frappe.pages.painel || {};

frappe.pages.painel.on_page_load = function (wrapper) {
	if (typeof advocacia !== "undefined" && advocacia.painel && advocacia.painel.init) {
		advocacia.painel.init(wrapper);
	} else {
		frappe.msgprint(__("Módulos do painel não carregados. Execute bench build --app advocacia."));
	}
};

frappe.pages.painel.on_page_hide = function () {
	$(document.body).removeClass("advocacia-painel-active");
};
