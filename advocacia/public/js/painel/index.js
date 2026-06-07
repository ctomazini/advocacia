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

(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var SA = advocacia.painel.saude;
	var AT = advocacia.painel.atencao;
	var AG = advocacia.painel.agenda;
	var A = advocacia.painel.audiencias;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.load = function (page, options) {
		options = options || {};
		var soft = !!options.soft;
		var section = options.section || null;
		var period = !!options.period;
		var scroll = soft ? AP._save_scroll(page) : null;

		if (!soft) {
			AP.mostrar_skeleton(page.painel_container);
		} else if (section) {
			page.painel_container.find("#painel-" + section).addClass("painel-section--updating");
		}

		var periodo = page.painel_periodo || 7;
		var list_limits = U.painel_merge_list_limits(page);
		frappe
			.xcall("advocacia.advocacia.painel_api.get_painel_data", {
				periodo_dias: periodo,
				list_limits: list_limits,
			})
			.then(function (data) {
				page.painel_data = data;
				if (section) {
					AP.patch_list_section(page.painel_container, section, data, page);
				} else if (period) {
					AP.patch_period_sections(page.painel_container, data, page);
				} else {
					AP.render(page.painel_container, data, page);
				}
				if (soft) {
					AP._restore_scroll(scroll);
				}
			})
			.catch(function (err) {
				if (soft && (section || period) && page.painel_data) {
					frappe.show_alert({
						message: __("Não foi possível atualizar o painel."),
						indicator: "red",
					});
				} else {
					AP.handle_error(page.painel_container, err);
				}
			})
			.finally(function () {
				page.painel_container.find(".painel-section--updating").removeClass(
					"painel-section--updating"
				);
			});
	};

	AP.render = function ($container, d, page, options) {
		options = options || {};
		var periodo = d.periodo_dias || page.painel_periodo || 7;
		var limits = d.list_limits || U.painel_merge_list_limits(page);
		var meta = d.list_meta || {};
		var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;
		page.painel_list_limits = limits;
		var content_class = options.animate === false ? " painel-content--stable" : "";
		var html = '<div class="painel-content' + content_class + '">';
		html += H.render_header(d.resumo, d.kpis, periodo, d.financeiro);
		html += H.render_filtros_painel(periodo);
		html += H.render_acoes_rapidas();
		html += '<div class="painel-zona-critica">';
		html += '<div class="painel-attention-duo">';
		html += AT.render(d.atencao);
		html +=
			'<div class="painel-proximo-evento-host">' +
			AG.render_proximo_evento(d.proximo_evento) +
			"</div>";
		html += "</div>";
		var agendaStrip = AG.render_day_strip(d.agenda_dias);
		if (agendaStrip) {
			html +=
				'<div class="painel-agenda-strip-host painel-dashboard-card">' +
				agendaStrip +
				"</div>";
		}
		html += '<div class="painel-saude-host painel-dashboard-card">';
		html += SA.render(d.saude_operacional);
		html += "</div></div>";
		html += T.render_timeline(d.timeline, periodo, meta.timeline, limits.timeline);
		html += T.render_comunicacoes_pendentes(
			d.comunicacoes_pendentes || d.ultimas_comunicacoes,
			periodo,
			meta.comunicacoes,
			limits.comunicacoes
		);
		html += K.render_indicadores_painel(
			d.centro_atencao,
			d.kpis,
			d.financeiro,
			horas,
			d.total_despesas_mes,
			periodo
		);
		html += '<div class="painel-zona-secundaria">';
		html += F.render_financeiro(d.financeiro, periodo);
		html += F.render_duo_honorarios_despesas(
			d.fee_installments,
			d.despesas_pendentes,
			d.total_despesas_mes,
			meta.fee_installments,
			meta.despesas,
			limits.fee_installments,
			limits.despesas
		);
		html += F.render_duo_custas_horas(
			d.custas_pendentes_repasse,
			d.total_custas_mes,
			horas,
			meta.custas,
			periodo,
			limits.custas
		);
		html += "</div>";
		html += "</div>";
		$container.html(html);
		F.painel_init_finance_chart($container, d.financeiro, page);
	};
})(advocacia.painel);
