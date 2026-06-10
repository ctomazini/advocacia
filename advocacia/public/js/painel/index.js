/* eslint-disable */
frappe.provide("advocacia.painel");

advocacia.painel.init = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel do Escritório"),
		single_column: true,
	});

	page.painel_container = $('<div class="painel-root"></div>').appendTo(page.main);
	advocacia.painel.utils.painel_polish_frappe_chrome();

	page.add_button(__("↺ Atualizar"), function () {
		advocacia.painel.load(page);
	});

	frappe.pages.painel.page = page;
	page.painel_periodo = 7;
	page.painel_list_limits = advocacia.painel.utils.painel_default_list_limits();
	advocacia.painel.bind_painel_filters(page.painel_container, page);
	advocacia.painel.bind_atencao_routes(page.painel_container, page);
	if (advocacia.painel.atencao && advocacia.painel.atencao.bind) {
		advocacia.painel.atencao.bind(page.painel_container, page);
	}
	if (advocacia.painel.agenda && advocacia.painel.agenda.bind) {
		advocacia.painel.agenda.bind(page.painel_container);
	}
	advocacia.painel.load(page);
};
