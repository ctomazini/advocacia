/* eslint-disable */
frappe.provide("advocacia.painel.kpis");

(function (AP) {
	var U = advocacia.painel.utils;

	AP.render_financial_kpis = function (kpis, fin, total_despesas, total_custas) {
		kpis = kpis || {};
		fin = fin || {};
		var vencido = kpis.fee_installments_vencidas || { count: 0, amount: 0 };
		var a_vencer = kpis.fee_installments_a_vencer_30d || { count: 0, amount: 0 };
		var recebido_mes = U.flt((kpis.recebido_mes && kpis.recebido_mes.amount) || 0);
		var despesas_mes = U.flt(total_despesas || 0);
		var custas_mes = U.flt(total_custas || 0);
		var saidas_mes = despesas_mes + custas_mes;
		var margem = recebido_mes - saidas_mes;
		var a_receber = U.flt(vencido.amount) + U.flt(a_vencer.amount);

		var cards = [
			{
				label: __("A receber (total)"),
				value: a_receber,
				sub: __("{0} itens", [U.cint(vencido.count) + U.cint(a_vencer.count)]),
				tone: "orange",
				icon: "wallet",
			},
			{
				label: __("Vencido"),
				value: U.flt(vencido.amount),
				sub: __("{0} parcelas", [U.cint(vencido.count)]),
				tone: "red",
				icon: "circle-alert",
			},
			{
				label: __("Honorários ativos"),
				value: U.cint(kpis.honorarios_ativos || 0),
				sub: __("acordos vigentes"),
				tone: "blue",
				icon: "file-text",
				plain: true,
			},
			{
				label: __("Custas em aberto"),
				value: U.cint(kpis.custas_abertas || 0),
				sub: __("aguardando repasse"),
				tone: "yellow",
				icon: "receipt",
				plain: true,
			},
			{
				label: __("Saídas do mês"),
				value: saidas_mes,
				sub: __("despesas + custas"),
				tone: "blue",
				icon: "wallet",
			},
			{
				label: __("Margem (mês)"),
				value: margem,
				sub: __("recebido − saídas"),
				tone: margem >= 0 ? "green" : "red",
				icon: "trending-up",
			},
		];

		var html = cards
			.map(function (card) {
				var valueHtml = card.plain
					? frappe.utils.escape_html(String(card.value))
					: U.fmt_currency(card.value);
				return (
					'<div class="painel-finance-kpi painel-finance-kpi--' +
					card.tone +
					'">' +
					'<div class="painel-finance-kpi__icon">' +
					U.painel_icon(card.icon) +
					"</div>" +
					'<div class="painel-finance-kpi__label">' +
					frappe.utils.escape_html(card.label) +
					"</div>" +
					'<div class="painel-finance-kpi__value">' +
					valueHtml +
					"</div>" +
					(card.sub
						? '<div class="painel-finance-kpi__meta">' +
						  frappe.utils.escape_html(card.sub) +
						  "</div>"
						: "") +
					"</div>"
				);
			})
			.join("");

		return '<div class="painel-finance-kpi-grid">' + html + "</div>";
	};
})(advocacia.painel.kpis = advocacia.painel.kpis || {});
