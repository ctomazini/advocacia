/* eslint-disable */
frappe.provide("advocacia.painel.hero");
(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.painel_context_html = function(resumo, kpis, periodo_dias, financeiro) {
	    resumo = resumo || {};
	    kpis = kpis || {};
	    financeiro = financeiro || {};
	    periodo_dias = U.cint(periodo_dias) || 7;

	    function part(text) {
	        return (
	            '<span class="painel-hero-context-part">' +
	            frappe.utils.escape_html(text) +
	            "</span>"
	        );
	    }

	    function money_part(label, value) {
	        return (
	            '<span class="painel-hero-context-part">' +
	            frappe.utils.escape_html(label + ": ") +
	            '<span class="painel-hero-money">' +
	            frappe.utils.escape_html(U.fmt_currency(value, true)) +
	            "</span></span>"
	        );
	    }

	    if (resumo.urgencia !== "alta") {
	        return part(
	            __("Visão operacional {0} — nenhuma urgência crítica no radar.", [
	                U.painel_periodo_enunciado(periodo_dias),
	            ])
	        );
	    }

	    var chunks = [];
	    if (resumo.audiencias_hoje) {
	        chunks.push(
	            part(
	                __("{0} audiência(s) hoje exigem presença ou preparo", [resumo.audiencias_hoje])
	            )
	        );
	    }
	    if (resumo.fee_installments_vencidas) {
	        chunks.push(
	            part(__("{0} parcela(s) vencida(s) aguardam recebimento", [resumo.fee_installments_vencidas]))
	        );
	    }
	    if (resumo.prazos_urgentes) {
	        chunks.push(
	            part(__("{0} prazo(s) com vencimento iminente", [resumo.prazos_urgentes]))
	        );
	    }
	    var previsto =
	        (financeiro.previsto_periodo && financeiro.previsto_periodo.amount) ||
	        resumo.previsto_periodo_valor ||
	        0;
	    if (previsto) {
	        chunks.push(money_part(U.painel_periodo_previsto_label(periodo_dias), previsto));
	    }
	    return chunks.join("");
	}

	AP.painel_greeting = function() {
	    var h = new Date().getHours();
	    if (h < 12) return __("Bom dia");
	    if (h < 18) return __("Boa tarde");
	    return __("Boa noite");
	}

	AP.render_header = function(resumo, kpis, periodo_dias, financeiro) {
	    resumo = resumo || {};
	    kpis = kpis || {};
	    financeiro = financeiro || {};
	    periodo_dias = U.cint(periodo_dias) || 7;
	    var urg = resumo.urgencia === "alta" ? "alta" : "normal";
	    var previsto_val =
	        resumo.previsto_periodo_valor != null
	            ? resumo.previsto_periodo_valor
	            : resumo.previsto_semana_valor ||
	              (financeiro.previsto_periodo && financeiro.previsto_periodo.amount) ||
	              (financeiro.previsto_semana && financeiro.previsto_semana.amount) ||
	              0;
	    var pulse_stats =
	        '<div class="painel-hero-pulse-stats">' +
	        '<span class="painel-hero-stat"><strong>' +
	        (resumo.audiencias_hoje || 0) +
	        "</strong> " +
	        __("audiência(s) hoje") +
	        "</span>";
	    pulse_stats +=
	        '<span class="painel-hero-stat"><strong>' +
	        (resumo.prazos_urgentes || 0) +
	        "</strong> " +
	        __("prazo(s) crítico(s)") +
	        "</span>";
	    pulse_stats +=
	        '<span class="painel-hero-stat"><strong>' +
	        (kpis.legal_tasks_pendentes || 0) +
	        "</strong> " +
	        __("tarefa(s) aberta(s)") +
	        "</span>" +
	        '<span class="painel-hero-stat"><strong>' +
	        (resumo.fee_installments_vencidas || 0) +
	        "</strong> " +
	        __("parcela(s) vencida(s)") +
	        "</span>" +
	        '<span class="painel-hero-stat painel-hero-stat--money"><strong class="painel-hero-money">' +
	        U.fmt_currency(previsto_val, true) +
	        "</strong> " +
	        U.painel_periodo_previsto_label(periodo_dias) +
	        "</span>";
	    pulse_stats += "</div>";
	    var pulse =
	        pulse_stats +
	        '<span class="painel-urgency-badge ' +
	        urg +
	        '">' +
	        (urg === "alta" ? __("Atenção hoje") : __("Operação estável")) +
	        "</span>";
	    return (
	        '<header class="painel-hero" id="painel-hero">' +
	        '<h1 class="painel-hero-greeting">' +
	        H.painel_greeting() +
	        "</h1>" +
	        '<p class="painel-hero-date">' +
	        frappe.utils.escape_html(resumo.data_hoje || "") +
	        "</p>" +
	        '<p class="painel-hero-context">' +
	        H.painel_context_html(resumo, kpis, periodo_dias, financeiro) +
	        "</p>" +
	        '<div class="painel-hero-pulse">' +
	        pulse +
	        "</div></header>"
	    );
	}

	AP.render_acoes_rapidas = function() {
	    var actions = [
	        { label: __("Client"), icon: "user-plus", dt: "Client" },
	        { label: __("Serviço"), icon: "folder-plus", dt: "Legal Case" },
	        { label: __("Audiência"), icon: "calendar-plus-2", dt: "Hearing" },
	        { label: __("Prazo"), icon: "clock-plus", dt: "Deadline" },
	        { label: __("Comunicação"), icon: "message-square-plus", dt: "Case Communication" },
	        { label: __("Legal Task"), icon: "list-plus", dt: "Legal Task" },
	        { label: __("Honorário"), icon: "file-plus", dt: "Fee Agreement" },
	        { label: __("Legal Payment"), icon: "circle-dollar-sign", dt: "Legal Payment" },
	        { label: __("Custa"), icon: "receipt", dt: "Court Cost" },
	        { label: __("Horas"), icon: "clock", dt: "Time Entry" },
	        { label: __("Despesa"), icon: "wallet", dt: "Office Expense" },
	    ];
	    var h =
	        '<div class="painel-actions-wrap">' +
	        '<p class="painel-actions-label">' +
	        __("Ações rápidas") +
	        "</p>" +
	        '<div class="painel-actions">';
	    actions.forEach(function (a) {
	        h +=
	            '<button type="button" class="painel-action-chip" data-new-dt="' +
	            a.dt +
	            '">' +
	            U.painel_icon(a.icon) +
	            "<span>" +
	            a.label +
	            "</span></button>";
	    });
	    h += "</div></div>";
	    return h;
	}

	AP.render_filtros_painel = function(periodo_atual) {
	    var opcoes_periodo = [
	        { dias: 1, label: __("Hoje") },
	        { dias: 7, label: __("7 dias") },
	        { dias: 15, label: __("15 dias") },
	        { dias: 30, label: __("30 dias") },
	    ];
	    var h =
	        '<div class="painel-periodo-bar" id="painel-periodo-bar">' +
	        '<div class="painel-filtro-group">' +
	        '<span class="painel-periodo-label">' +
	        U.painel_periodo_scope_label(periodo_atual) +
	        "</span>" +
	        '<div class="painel-periodo-filters">';
	    opcoes_periodo.forEach(function (op) {
	        h +=
	            '<button type="button" class="painel-periodo-btn' +
	            (periodo_atual === op.dias ? " active" : "") +
	            '" data-periodo="' +
	            op.dias +
	            '">' +
	            op.label +
	            "</button>";
	    });
	    h += "</div></div></div>";
	    return h;
	}

})(advocacia.painel.hero = advocacia.painel.hero || {});
