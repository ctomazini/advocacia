/* eslint-disable */
frappe.provide("advocacia.painel.financeiro");
(function (AP) {
	var U = advocacia.painel.utils;
	var F = advocacia.painel.financeiro;

	AP.render_composition = function (fin, periodo_dias) {
		if (!fin) return "";
		periodo_dias = U.cint(periodo_dias) || 7;
		var max_val = 1;
		(fin.grafico || []).forEach(function (g) {
			if (U.flt(g.amount) > max_val) max_val = U.flt(g.amount);
		});
		var chart_rows = (fin.grafico || [])
			.map(function (g) {
				var pct = Math.max(4, Math.round((U.flt(g.amount) / max_val) * 100));
				return (
					'<div class="painel-chart-row">' +
					'<span class="painel-chart-label">' +
					frappe.utils.escape_html(g.label) +
					"</span>" +
					'<div class="painel-chart-track"><div class="painel-chart-fill ' +
					(g.tone || "neutral") +
					'" style="width:' +
					pct +
					'%"></div></div>' +
					'<span class="painel-chart-amt">' +
					U.fmt_currency(g.amount) +
					"</span></div>"
				);
			})
			.join("");
		var taxa = fin.taxa_recebimento || 0;
		return (
			'<div class="painel-finance-block" id="painel-finance-composition">' +
			'<div class="painel-section-head"><div><h2 class="painel-section-title">' +
			__("Composição") +
			"</h2>" +
			'<p class="painel-section-sub">' +
			__("Recebíveis do mês · {0}", [U.painel_periodo_enunciado(periodo_dias)]) +
			"</p></div></div>" +
			'<div class="painel-panel painel-finance-composition-panel">' +
			'<div class="painel-chart painel-chart--percent">' +
			'<div class="painel-chart-row">' +
			'<span class="painel-chart-label">' +
			__("Recebido") +
			"</span>" +
			'<div class="painel-chart-track"><div class="painel-chart-fill success" style="width:' +
			Math.max(4, Math.min(100, taxa)) +
			'%"></div></div>' +
			'<span class="painel-chart-amt">' +
			taxa +
			"%</span></div>" +
			chart_rows +
			"</div></div></div>"
		);
	};

	AP.render_financeiro = function (fin, periodo_dias) {
		return AP.render_composition(fin, periodo_dias);
	};

	AP.build_parcelas_criticas = function(parcelas, limit) {
	    if (!parcelas || !parcelas.length) return "";
	    var sorted = parcelas.slice().sort(function (a, b) {
	        if (U._is_vencido(a.status) && !U._is_vencido(b.status)) return -1;
	        if (U._is_vencido(b.status) && !U._is_vencido(a.status)) return 1;
	        return (a.dias_atraso || 0) > (b.dias_atraso || 0) ? -1 : 1;
	    });
	    return sorted
	        .slice(0, limit)
	        .map(function (p) {
	            var btn = "";
	            if (U._pagamento_pode_receber(p.status)) {
	                btn =
	                    '<button type="button" class="painel-btn-recebida" data-pagamento="' +
	                    frappe.utils.escape_html(p.name || "") +
	                    '">✓ ' +
	                    __("Recebido") +
	                    "</button>";
	            }
	            return (
	                '<div class="painel-op-item painel-parcela-critica" data-dt="Legal Payment" data-dn="' +
	                frappe.utils.escape_html(p.name || "") +
	                '" data-acordo="' +
	                frappe.utils.escape_html(p.parent || "") +
	                '">' +
	                '<div class="painel-op-body"><div class="painel-op-title">' +
	                frappe.utils.escape_html(p.client_nome || "—") +
	                '</div><div class="painel-op-sub">' +
	                U.fmt_currency(p.total_amount) +
	                " · " +
	                U.fmt_date_iso(p.due_date) +
	                "</div></div>" +
	                '<div class="painel-op-side">' +
	                U.status_pill(p.status) +
	                btn +
	                "</div></div>"
	            );
	        })
	        .join("");
	}

	AP.render_duo_honorarios_despesas = function(
	    parcelas,
	    despesas,
	    total_mes,
	    meta_parcelas,
	    meta_despesas,
	    limit_parcelas,
	    limit_despesas
	) {
	    return (
	        '<div class="painel-duo-grid" id="painel-duo-financeiro">' +
	        F.render_parcelas(parcelas, true, meta_parcelas, limit_parcelas) +
	        F.render_despesas(despesas, total_mes, true, meta_despesas, limit_despesas) +
	        "</div>"
	    );
	}

	AP.render_duo_custas_horas = function(custas, total_mes, horas, meta_custas, periodo_dias, limit_custas) {
	    return (
	        '<div class="painel-duo-grid" id="painel-duo-secundario">' +
	        F.render_custas(custas, total_mes, true, meta_custas, limit_custas) +
	        F.render_horas_semana(horas, true, periodo_dias) +
	        "</div>"
	    );
	}

	AP.render_parcelas = function(parcelas, compact, list_meta, list_limit) {
	    var meta_html = U.painel_list_meta_html(list_meta, list_limit);
	    var h =
	        '<section class="painel-section' +
	        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
	        '" id="painel-parcelas"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Honorários em aberto") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Pendentes e vencidos") +
	        "</p></div>" +
	        '<div class="painel-section-head-actions">' +
	        U.render_list_limit_controls("fee_installments", list_limit) +
	        meta_html +
	        '<span class="painel-section-link" data-route-list="Legal Payment">' +
	        __("Ver todos") +
	        "</span></div></div>";
	    if (!parcelas || !parcelas.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_empty_state(
	                "tick",
	                __("Honorários em dia"),
	                __("Não há parcelas pendentes ou vencidas no momento.")
	            ) +
	            "</div></section>"
	        );
	    }
	    h += '<div class="painel-panel">';
	    parcelas.forEach(function (p) {
	        var prazo_txt = "";
	        if (U._is_vencido(p.status) && p.dias_atraso > 0) {
	            prazo_txt = __("Atraso {0}d", [p.dias_atraso]);
	        } else if (p.status === "Pendente") {
	            prazo_txt = p.dias_para_vencer === 0 ? __("Hoje") : __("Em {0}d", [p.dias_para_vencer]);
	        }
	        var btn = "";
	        if (U._pagamento_pode_receber(p.status)) {
	            btn =
	                '<button type="button" class="painel-btn-recebida" data-pagamento="' +
	                frappe.utils.escape_html(p.name || "") +
	                '">✓ ' +
	                __("Recebido") +
	                "</button>";
	        }
	        h +=
	            '<div class="painel-list-item painel-parcela-card painel-row-acordo" data-dt="Legal Payment" data-dn="' +
	            frappe.utils.escape_html(p.name || "") +
	            '" data-acordo="' +
	            frappe.utils.escape_html(p.parent || "") +
	            '">' +
	            '<div class="painel-parcela-main"><div class="painel-op-title">' +
	            frappe.utils.escape_html(p.client_nome || "—") +
	            '</div><div class="painel-op-sub">' +
	            frappe.utils.escape_html(p.legal_case_titulo || p.legal_case_tipo || "") +
	            (p.case_number ? " · " + frappe.utils.escape_html(p.case_number) : "") +
	            "</div>" +
	            '<div class="painel-muted">' +
	            U.fmt_date_iso(p.due_date) +
	            (prazo_txt ? " · " + prazo_txt : "") +
	            "</div>" +
	            U.status_pill(p.status) +
	            "</div>" +
	            '<div class="painel-list-side">' +
	            '<div class="painel-list-valor ' +
	            (U._is_vencido(p.status) ? "danger" : "warn") +
	            '">' +
	            U.fmt_currency(p.total_amount) +
	            "</div>" +
	            btn +
	            "</div></div>";
	    });
	    h += "</div></section>";
	    return h;
	}

	AP.render_despesas = function(despesas, total_mes, compact, list_meta, list_limit) {
	    var meta_html = U.painel_list_meta_html(list_meta, list_limit);
	    var h =
	        '<section class="painel-section' +
	        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
	        '" id="painel-despesas"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Despesas") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Pendentes · mês calendário: {0}", [U.fmt_currency(total_mes || 0, true)]) +
	        "</p></div>" +
	        '<div class="painel-section-head-actions">' +
	        U.render_list_limit_controls("despesas", list_limit) +
	        meta_html +
	        '<span class="painel-section-link" data-route-list="Office Expense">' +
	        __("Ver todas") +
	        "</span></div></div>";

	    if (!despesas || !despesas.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_empty_state(
	                "wallet",
	                __("Nenhuma despesa pendente"),
	                __("Despesas operacionais aparecerão aqui quando cadastradas.")
	            ) +
	            "</div></section>"
	        );
	    }

	    h += '<div class="painel-panel"><div class="painel-schedule-list">';
	    despesas.forEach(function (d) {
	        var tone = d.status === "Atrasado" ? "danger" : "warn";
	        var badge =
	            d.status === "Atrasado"
	                ? '<span class="indicator-pill red">' + __("Atrasado") + "</span>"
	                : '<span class="indicator-pill orange">' + __("Pendente") + "</span>";
	        h +=
	            '<div class="painel-list-item painel-schedule-item painel-row-despesa" data-dt="Office Expense" data-dn="' +
	            frappe.utils.escape_html(d.name || "") +
	            '">' +
	            '<div class="painel-schedule-main">' +
	            '<div class="painel-op-title">' +
	            frappe.utils.escape_html(d.description || d.name) +
	            "</div>" +
	            '<div class="painel-op-sub">' +
	            frappe.utils.escape_html(d.category || "") +
	            (d.due_date
	                ? " · " + frappe.utils.escape_html(frappe.datetime.str_to_user(d.due_date))
	                : "") +
	            "</div>" +
	            badge +
	            "</div>" +
	            '<div class="painel-list-side">' +
	            '<div class="painel-list-valor ' +
	            tone +
	            '">' +
	            U.fmt_currency(d.amount) +
	            "</div></div></div>";
	    });
	    h += "</div></div></section>";
	    return h;
	}

	AP.render_custas = function(custas, total_mes, compact, list_meta, list_limit) {
	    var meta_html = U.painel_list_meta_html(list_meta, list_limit);
	    var h =
	        '<section class="painel-section' +
	        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
	        '" id="painel-custas"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Custas") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Repasse · mês calendário: {0}", [U.fmt_currency(total_mes || 0, true)]) +
	        "</p></div>" +
	        '<div class="painel-section-head-actions">' +
	        U.render_list_limit_controls("custas", list_limit) +
	        meta_html +
	        '<span class="painel-section-link" data-route-list="Court Cost">' +
	        __("Ver todas") +
	        "</span></div></div>";

	    if (!custas || !custas.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_empty_state(
	                "receipt",
	                __("Nenhuma custa pendente de repasse"),
	                __("Custas pagas marcadas para repasse aparecerão aqui.")
	            ) +
	            "</div></section>"
	        );
	    }

	    h += '<div class="painel-panel"><div class="painel-schedule-list">';
	    custas.forEach(function (c) {
	        h +=
	            '<div class="painel-list-item painel-schedule-item painel-row-custa" data-dt="Court Cost" data-dn="' +
	            frappe.utils.escape_html(c.name || "") +
	            '">' +
	            '<div class="painel-schedule-main">' +
	            '<div class="painel-op-title">' +
	            frappe.utils.escape_html(c.description || c.name) +
	            "</div>" +
	            '<div class="painel-op-sub">' +
	            frappe.utils.escape_html(c.type || "") +
	            (c.legal_case_titulo ? " · " + frappe.utils.escape_html(c.legal_case_titulo) : "") +
	            "</div>" +
	            '<span class="indicator-pill blue">' + __("Aguardando repasse") + "</span>" +
	            "</div>" +
	            '<div class="painel-list-side">' +
	            '<div class="painel-list-valor warn">' +
	            U.fmt_currency(c.amount) +
	            "</div></div></div>";
	    });
	    h += "</div></div></section>";
	    return h;
	}

	AP.render_horas_semana = function(horas, compact, periodo_dias) {
	    periodo_dias = U.cint(periodo_dias) || 7;
	    return (
	        '<section class="painel-section' +
	        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
	        '" id="painel-horas">' +
	        '<div class="painel-section-head"><div><h2 class="painel-section-title">' +
	        __("Horas") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Registradas {0}", [U.painel_periodo_enunciado(periodo_dias)]) +
	        "</p></div>" +
	        '<span class="painel-section-link" data-route-list="Time Entry">' +
	        __("Ver todas") +
	        "</span></div>" +
	        '<div class="painel-panel painel-horas-panel">' +
	        '<div class="painel-atencao-count">' +
	        (horas || 0).toFixed(1) +
	        " h</div></div></section>"
	    );
	}

	AP.render_secundario = function(title, icon, body, section_id, emptyTitle, emptyHint, list_doctype) {
	    var foot = "";
	    if (list_doctype && body) {
	        foot =
	            '<div class="painel-section-foot">' +
	            '<span class="painel-section-foot-link" data-route-list="' +
	            frappe.utils.escape_html(list_doctype) +
	            '">' +
	            __("Ver todos") +
	            "</span></div>";
	    }
	    return (
	        '<section class="painel-section painel-section--secondary" id="' +
	        section_id +
	        '"><div class="painel-section-head">' +
	        "<h2 class='painel-section-title'>" +
	        title +
	        "</h2></div>" +
	        '<div class="painel-panel">' +
	        (body
	            ? '<div class="painel-schedule-list">' + body + "</div>" + foot
	            : U.render_empty_state(icon, emptyTitle, emptyHint)) +
	        "</div></section>"
	    );
	}

})(advocacia.painel.financeiro = advocacia.painel.financeiro || {});
