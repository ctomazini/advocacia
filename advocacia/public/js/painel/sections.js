/* eslint-disable */
(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var SA = advocacia.painel.saude;
	var AT = advocacia.painel.atencao;
	var AG = advocacia.painel.agenda;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;
	var OP = advocacia.painel.operational;

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
			case "proximo_evento":
				return AG.render_proximo_evento(d.proximo_evento);
			case "finance_head":
				if (!d.financeiro) {
					return "";
				}
				return (
					'<div class="painel-finance-stack">' +
					'<div class="painel-finance-stack__health">' +
					SA.render(d.saude_operacional, { compact: true }) +
					"</div>" +
					'<div class="painel-finance-stack__kpis">' +
					K.render_financial_kpis(
						d.kpis,
						d.financeiro,
						d.total_despesas_mes,
						d.total_custas_mes
					) +
					"</div>" +
					F.render_composition(d.financeiro, periodo) +
					"</div>"
				);
			case "timeline":
				return T.render_timeline(d.timeline, periodo, meta.timeline, limits.timeline);
			case "active_cases":
				return OP.render(d.active_cases, meta.active_cases, limits.active_cases);
			case "comunicacoes":
				return T.render_comunicacoes_pendentes(
					d.comunicacoes_pendentes || d.ultimas_comunicacoes,
					periodo,
					meta.comunicacoes,
					limits.comunicacoes
				);
			case "finance_composition":
				return F.render_composition(d.financeiro, periodo);
			case "financeiro":
				return F.render_composition(d.financeiro, periodo);
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
			case "active_cases":
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
