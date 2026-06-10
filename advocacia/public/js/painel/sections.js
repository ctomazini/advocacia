/* eslint-disable */
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

	AP._period_section_html = function (list_key, d, page) {
		var periodo = d.periodo_dias || page.painel_periodo || 7;
		var limits = d.list_limits || U.painel_merge_list_limits(page);
		var meta = d.list_meta || {};
		var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;

		switch (list_key) {
			case "hero":
				return H.render_header(d.summary, d.kpis, periodo, d.financeiro);
			case "centro_atencao":
				return AT.render(d.atencao);
			case "agenda_dias":
				return (
					'<div class="painel-agenda-strip-host painel-dashboard-card">' +
					AG.render_day_strip(d.agenda_dias) +
					"</div>"
				);
			case "proximo_evento":
				return AG.render_proximo_evento(d.proximo_evento);
			case "prox_audiencia":
				return AG.render_proximo_evento(d.proximo_evento);
			case "saude_operacional":
				return (
					'<div class="painel-saude-host painel-dashboard-card">' +
					SA.render(d.saude_operacional) +
					"</div>"
				);
			case "timeline":
				return T.render_timeline(d.timeline, periodo, meta.timeline, limits.timeline);
			case "comunicacoes":
				return T.render_comunicacoes_pendentes(
					d.comunicacoes_pendentes || d.ultimas_comunicacoes,
					periodo,
					meta.comunicacoes,
					limits.comunicacoes
				);
			case "indicadores":
				return K.render_indicadores_painel(
					d.centro_atencao,
					d.kpis,
					d.financeiro,
					horas,
					d.total_despesas_mes,
					periodo
				);
			case "financeiro":
				return F.render_financeiro(d.financeiro, periodo);
			case "duo_financeiro":
				return F.render_duo_honorarios_despesas(
					d.fee_installments,
					d.despesas_pendentes,
					d.total_despesas_mes,
					meta.fee_installments,
					meta.despesas,
					limits.fee_installments,
					limits.despesas
				);
			case "duo_secundario":
				return F.render_duo_custas_horas(
					d.custas_pendentes_repasse,
					d.total_custas_mes,
					horas,
					meta.custas,
					periodo,
					limits.custas
				);
			default:
				return "";
		}
	};

	AP._list_section_html = function (list_key, d, page) {
		var limits = d.list_limits || U.painel_merge_list_limits(page);
		var meta = d.list_meta || {};

		switch (list_key) {
			case "timeline":
			case "comunicacoes":
				return AP._period_section_html(list_key, d, page);
			case "fee_installments":
				return F.render_parcelas(
					d.fee_installments,
					true,
					meta.fee_installments,
					limits.fee_installments
				);
			case "despesas":
				return F.render_despesas(
					d.despesas_pendentes,
					d.total_despesas_mes,
					true,
					meta.despesas,
					limits.despesas
				);
			case "custas":
				return F.render_custas(
					d.custas_pendentes_repasse,
					d.total_custas_mes,
					true,
					meta.custas,
					limits.custas
				);
			default:
				return "";
		}
	};
})(advocacia.painel);
