/* eslint-disable */
frappe.provide("advocacia.painel.kpis");
(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var A = advocacia.painel.audiencias;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.render_centro_atencao = function(centro, kpis, fin, horas, total_despesas, periodo_dias) {
	    centro = centro || {};
	    kpis = kpis || {};
	    fin = fin || {};
	    periodo_dias = U.cint(periodo_dias) || 7;

	    function card(it) {
	        return (
	            '<div class="painel-atencao-card tone-' +
	            it.tone +
	            '" data-atencao-route="' +
	            it.route +
	            '">' +
	            '<div class="painel-atencao-icon">' +
	            U.painel_icon(it.icon) +
	            "</div>" +
	            '<div class="painel-atencao-body">' +
	            '<div class="painel-atencao-count">' +
	            frappe.utils.escape_html(String(it.count)) +
	            "</div>" +
	            '<div class="painel-atencao-label">' +
	            frappe.utils.escape_html(it.label) +
	            "</div>" +
	            (it.meta
	                ? '<div class="painel-atencao-meta">' +
	                  frappe.utils.escape_html(String(it.meta)) +
	                  "</div>"
	                : "") +
	            "</div></div>"
	        );
	    }

	    function group(title, items) {
	        var cards = items.map(card).join("");
	        if (!cards) return "";
	        return (
	            '<div class="painel-centro-group">' +
	            '<h3 class="painel-centro-group-title">' +
	            frappe.utils.escape_html(title) +
	            "</h3>" +
	            '<div class="painel-centro-grid">' +
	            cards +
	            "</div></div>"
	        );
	    }

	    var urgentes = [
	        {
	            tone: "red",
	            icon: "calendar-days",
	            count: centro.audiencias_hoje || 0,
	            label: __("Audiências hoje"),
	            route: "audiencias_hoje",
	        },
	        {
	            tone: "orange",
	            icon: "calendar-clock",
	            count: centro.audiencias_amanha || 0,
	            label: __("Amanhã"),
	            route: "audiencias_amanha",
	        },
	        {
	            tone: "red",
	            icon: "alarm-clock",
	            count: centro.prazos_vencidos || 0,
	            label: __("Prazos vencidos"),
	            route: "prazos_vencidos",
	        },
	        {
	            tone: "orange",
	            icon: "timer",
	            count: centro.prazos_proximos_3d || 0,
	            label: __("Prazos 3 dias"),
	            route: "prazos_proximos",
	        },
	        {
	            tone: "yellow",
	            icon: "list-todo",
	            count: centro.legal_tasks_atrasadas || 0,
	            label: __("Legal Tasks atrasadas"),
	            route: "tarefas_atrasadas",
	        },
	        {
	            tone: "red",
	            icon: "circle-dollar-sign",
	            count: (centro.fee_installments_vencidas && centro.fee_installments_vencidas.count) || 0,
	            label: __("Parcelas vencidas"),
	            meta: U.fmt_currency((centro.fee_installments_vencidas && centro.fee_installments_vencidas.amount) || 0, true),
	            route: "parcelas_vencidas",
	        },
	    ];

	    var no_periodo = [
	        {
	            tone: "orange",
	            icon: "wallet",
	            count: (centro.payments_periodo && centro.payments_periodo.count) || 0,
	            label: U.painel_periodo_a_receber_label(periodo_dias),
	            meta: U.fmt_currency((centro.payments_periodo && centro.payments_periodo.amount) || 0, true),
	            route: "payments_periodo",
	        },
	        {
	            tone: "green",
	            icon: "trending-up",
	            count: (centro.recebimentos_periodo && centro.recebimentos_periodo.count) || 0,
	            label: U.painel_periodo_recebidos_label(periodo_dias),
	            meta: U.fmt_currency((centro.recebimentos_periodo && centro.recebimentos_periodo.amount) || 0, true),
	            route: "recebimentos_periodo",
	        },
	    ];

	    return (
	        '<section class="painel-section painel-centro-atencao painel-priority-max" id="painel-centro-atencao">' +
	        '<div class="painel-centro-shell">' +
	        '<div class="painel-section-head painel-centro-head"><div><h2 class="painel-section-title">' +
	        __("Centro de Atenção") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("O que exige sua atenção agora — {0}", [U.painel_periodo_enunciado(periodo_dias)]) +
	        "</p></div></div>" +
	        '<div class="painel-centro-groups">' +
	        group(__("Urgente"), urgentes) +
	        group(__("No período ({0})", [U.painel_periodo_label(periodo_dias)]), no_periodo) +
	        "</div></div></section>"
	    );
	}

	AP.painel_build_indicadores_items = function(centro, kpis, fin, horas, total_despesas, periodo_dias) {
	    centro = centro || {};
	    kpis = kpis || {};
	    fin = fin || {};
	    periodo_dias = U.cint(periodo_dias) || 7;
	    return [
	        {
	            tone: "blue",
	            icon: "calendar",
	            count: centro.audiencias_periodo || kpis.audiencias_semana || 0,
	            label: __("Audiências ({0})", [U.painel_periodo_label(periodo_dias)]),
	            route: "audiencias_periodo",
	        },
	        {
	            tone: "orange",
	            icon: "time",
	            count: centro.prazos_urgentes || kpis.prazos_urgentes || 0,
	            label: __("Prazos críticos"),
	            route: "prazos_criticos",
	        },
	        {
	            tone: "yellow",
	            icon: "checklist",
	            count: centro.legal_tasks_pendentes || kpis.legal_tasks_pendentes || 0,
	            label: __("Legal Tasks abertas"),
	            route: "tarefas_pendentes",
	        },
	        {
	            tone: "green",
	            icon: "banknote",
	            count: U.fmt_currency((kpis.recebido_mes && kpis.recebido_mes.amount) || 0, true),
	            label: __("Receita mês"),
	            route: "receita_mes",
	        },
	        {
	            tone: "blue",
	            icon: "file-text",
	            count: centro.honorarios_ativos || kpis.honorarios_ativos || 0,
	            label: __("Honorários ativos"),
	            route: "honorarios_ativos",
	        },
	        {
	            tone: "blue",
	            icon: "clock",
	            count: (horas || 0).toFixed(1) + " h",
	            label: U.painel_horas_label(periodo_dias),
	            route: "horas",
	        },
	        {
	            tone: "gray",
	            icon: "users",
	            count: centro.total_clientes || kpis.total_clientes || 0,
	            label: __("Clients"),
	            route: "clientes",
	        },
	        {
	            tone: "green",
	            icon: "percent",
	            count: (fin.taxa_recebimento || kpis.taxa_recebimento || 0) + "%",
	            label: __("Taxa receb."),
	            route: "taxa_recebimento",
	        },
	        {
	            tone: "blue",
	            icon: "briefcase",
	            count: centro.legal_cases_ativos || kpis.legal_cases_ativos || 0,
	            label: __("Processos"),
	            route: "processos_ativos",
	        },
	        {
	            tone: "orange",
	            icon: "receipt",
	            count: centro.custas_abertas || kpis.custas_abertas || 0,
	            label: __("Custas abertas"),
	            route: "custas_abertas",
	        },
	        {
	            tone: "orange",
	            icon: "wallet",
	            count: U.fmt_currency(total_despesas || 0, true),
	            label: __("Despesas mês"),
	            route: "despesas_mes",
	        },
	    ];
	}

	AP.render_indicadores_painel = function(centro, kpis, fin, horas, total_despesas, periodo_dias) {
	    var items = K.painel_build_indicadores_items(
	        centro,
	        kpis,
	        fin,
	        horas,
	        total_despesas,
	        periodo_dias
	    );

	    function card(it) {
	        return (
	            '<div class="painel-atencao-card tone-' +
	            it.tone +
	            '" data-atencao-route="' +
	            it.route +
	            '">' +
	            '<div class="painel-atencao-icon">' +
	            U.painel_icon(it.icon) +
	            "</div>" +
	            '<div class="painel-atencao-body">' +
	            '<div class="painel-atencao-count">' +
	            frappe.utils.escape_html(String(it.count)) +
	            "</div>" +
	            '<div class="painel-atencao-label">' +
	            frappe.utils.escape_html(it.label) +
	            "</div></div></div>"
	        );
	    }

	    return (
	        '<section class="painel-section painel-priority-medium" id="painel-indicadores">' +
	        '<div class="painel-section-head"><div><h2 class="painel-section-title">' +
	        __("Indicadores") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Visão consolidada {0}", [U.painel_periodo_enunciado(periodo_dias)]) +
	        "</p></div></div>" +
	        '<div class="painel-centro-grid">' +
	        items.map(card).join("") +
	        "</div></section>"
	    );
	}

	AP.painel_calc_saude_operacional = function(centro, kpis, fin) {
	    centro = centro || {};
	    kpis = kpis || {};
	    fin = fin || {};
	    var vencidos =
	        (centro.prazos_vencidos || 0) +
	        ((centro.fee_installments_vencidas && centro.fee_installments_vencidas.count) || 0) +
	        (centro.legal_tasks_atrasadas || 0);
	    var pendentes = centro.legal_tasks_pendentes || kpis.legal_tasks_pendentes || 0;
	    var previstos =
	        (centro.payments_periodo && centro.payments_periodo.count) ||
	        (fin.previsto_periodo && fin.previsto_periodo.count) ||
	        0;
	    var honorarios = centro.honorarios_ativos || kpis.honorarios_ativos || 0;
	    var atencao =
	        (centro.prazos_proximos_3d || 0) + (centro.prazos_urgentes || kpis.prazos_urgentes || 0);
	    var penal = Math.min(
	        85,
	        vencidos * 4 + atencao * 1.5 + (centro.legal_tasks_atrasadas || 0) * 2
	    );
	    var score = Math.round(Math.max(0, Math.min(100, 100 - penal)));
	    var label =
	        score >= 85
	            ? __("Excelente")
	            : score >= 70
	              ? __("Boa")
	              : score >= 50
	                ? __("Atenção")
	                : __("Crítica");
	    var tone = score >= 85 ? "green" : score >= 70 ? "blue" : score >= 50 ? "orange" : "red";
	    return {
	        score: score,
	        label: label,
	        tone: tone,
	        vencidos: vencidos,
	        pendentes: pendentes,
	        previstos: previstos,
	        honorarios: honorarios,
	    };
	}

	AP.render_saude_operacional = function(centro, kpis, fin) {
	    var s = K.painel_calc_saude_operacional(centro, kpis, fin);
	    var circumference = 2 * Math.PI * 36;
	    var offset = circumference - (circumference * s.score) / 100;
	    return (
	        '<div class="painel-saude-card painel-priority-max" id="painel-saude-operacional">' +
	        '<div class="painel-saude-head">' +
	        '<span class="painel-saude-badge tone-' +
	        s.tone +
	        '">' +
	        U.painel_icon("activity") +
	        "</span>" +
	        '<h3 class="painel-saude-title">' +
	        __("Saúde Operacional") +
	        "</h3></div>" +
	        '<div class="painel-saude-body">' +
	        '<div class="painel-saude-score-wrap">' +
	        '<div class="painel-saude-ring">' +
	        '<svg viewBox="0 0 88 88" aria-hidden="true">' +
	        '<circle class="painel-saude-ring-bg" cx="44" cy="44" r="36"></circle>' +
	        '<circle class="painel-saude-ring-fill tone-' +
	        s.tone +
	        '" cx="44" cy="44" r="36" stroke-dasharray="' +
	        circumference +
	        '" stroke-dashoffset="' +
	        offset +
	        '"></circle></svg>' +
	        '<div class="painel-saude-score-text">' +
	        '<span class="painel-saude-score-num">' +
	        s.score +
	        "%</span>" +
	        '<span class="painel-saude-score-label">' +
	        frappe.utils.escape_html(s.label) +
	        "</span></div></div>" +
	        '<div class="painel-saude-summary">' +
	        "<h4>" +
	        frappe.utils.escape_html(s.label) +
	        "</h4>" +
	        "<p>" +
	        __("Consolidado a partir dos indicadores operacionais já exibidos no painel.") +
	        "</p></div></div>" +
	        '<div class="painel-saude-rows">' +
	        '<div class="painel-saude-row"><span class="painel-saude-dot red"></span><span><strong>' +
	        s.vencidos +
	        "</strong> " +
	        __("itens vencidos ou críticos") +
	        "</span></div>" +
	        '<div class="painel-saude-row"><span class="painel-saude-dot orange"></span><span><strong>' +
	        s.pendentes +
	        "</strong> " +
	        __("tarefas pendentes") +
	        "</span></div>" +
	        '<div class="painel-saude-row"><span class="painel-saude-dot green"></span><span><strong>' +
	        s.previstos +
	        "</strong> " +
	        __("recebimentos previstos") +
	        "</span></div>" +
	        '<div class="painel-saude-row"><span class="painel-saude-dot green"></span><span><strong>' +
	        s.honorarios +
	        "</strong> " +
	        __("honorários ativos") +
	        "</span></div></div></div></div>"
	    );
	}

	AP.render_kpis = function(k) {
	    if (!k) return "";
	    var items = [
	        {
	            key: "vencidas",
	            label: __("Parcelas vencidas"),
	            value: U.fmt_currency((k.fee_installments_vencidas && k.fee_installments_vencidas.amount) || 0),
	            meta: __("{0} parcela(s)", [(k.fee_installments_vencidas && k.fee_installments_vencidas.count) || 0]),
	            urgent: true,
	        },
	        {
	            key: "recebido",
	            label: __("Recebido este mês"),
	            value: U.fmt_currency(k.recebido_mes.amount),
	            meta: __("{0} recebida(s)", [k.recebido_mes.count]),
	            positive: true,
	        },
	        {
	            key: "previsto",
	            label: __("Previsto no mês"),
	            value: U.fmt_currency((k.previsto_mes && k.previsto_mes.amount) || 0),
	            meta: __("{0} pendente(s)", [(k.previsto_mes && k.previsto_mes.count) || 0]),
	            warn: true,
	        },
	        {
	            key: "audiencias",
	            label: __("Audiências hoje"),
	            value: String(k.audiencias_hoje != null ? k.audiencias_hoje : 0),
	            meta: __("{0} na semana", [k.audiencias_semana]),
	        },
	        {
	            key: "prazos",
	            label: __("Prazos urgentes"),
	            value: String(k.prazos_urgentes),
	            meta: __("até 3 dias"),
	            urgent: k.prazos_urgentes > 0,
	        },
	        {
	            key: "servicos",
	            label: __("Serviços ativos"),
	            value: String(k.legal_cases_ativos),
	            meta: __("{0} clientes", [k.total_clientes]),
	        },
	    ];
	    var h =
	        '<section class="painel-section"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Indicadores") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Visão rápida do escritório") +
	        "</p></div></div>" +
	        '<div class="painel-kpi-grid">';
	    items.forEach(function (item) {
	        var cls = "painel-kpi";
	        if (item.urgent) cls += " urgent";
	        if (item.positive) cls += " positive";
	        if (item.warn) cls += " warn";
	        h +=
	            '<div class="' +
	            cls +
	            '" data-kpi="' +
	            item.key +
	            '">' +
	            '<div class="painel-kpi-label">' +
	            item.label +
	            "</div>" +
	            '<div class="painel-kpi-value">' +
	            item.value +
	            "</div>" +
	            '<div class="painel-kpi-meta">' +
	            (item.meta || "") +
	            "</div></div>";
	    });
	    h += "</div></section>";
	    return h;
	}

	AP.render_kpis_operacionais = function(k, fin, horas, total_despesas, total_custas, custas_list) {
	    if (!k) return "";
	    fin = fin || {};
	    var row1 = [
	        { label: __("Audiências da semana"), value: String(k.audiencias_semana || 0), route: "audiencias_semana" },
	        { label: __("Prazos críticos"), value: String(k.prazos_urgentes || 0), urgent: k.prazos_urgentes > 0, route: "prazos_criticos" },
	        { label: __("Legal Tasks pendentes"), value: String(k.legal_tasks_pendentes || 0), route: "tarefas_pendentes" },
	        {
	            label: __("Recebimentos do período"),
	            value: U.fmt_currency((k.recebido_periodo && k.recebido_periodo.amount) || 0),
	            positive: true,
	            route: "recebimentos_periodo",
	        },
	    ];
	    var row2 = [
	        { label: __("Receita do mês"), value: U.fmt_currency((k.recebido_mes && k.recebido_mes.amount) || 0), positive: true, route: "receita_mes" },
	        { label: __("Honorários ativos"), value: String(k.honorarios_ativos || 0), route: "honorarios_ativos" },
	        { label: __("Horas registradas"), value: (horas || 0).toFixed(1) + " h", route: "horas" },
	        { label: __("Clients ativos"), value: String(k.total_clientes || 0), route: "clientes" },
	    ];
	    var row3 = [
	        { label: __("Taxa de recebimento"), value: (fin.taxa_recebimento || k.taxa_recebimento || 0) + "%", route: "taxa_recebimento" },
	        { label: __("Processos ativos"), value: String(k.legal_cases_ativos || 0), route: "processos_ativos" },
	        {
	            label: __("Custas abertas"),
	            value: String(k.custas_abertas || (custas_list && custas_list.length) || 0),
	            warn: (k.custas_abertas || 0) > 0,
	            route: "custas_abertas",
	        },
	        { label: __("Despesas do mês"), value: U.fmt_currency(total_despesas || 0), route: "despesas_mes" },
	    ];

	    var h =
	        '<section class="painel-section" id="painel-kpis"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("KPIs Operacionais") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Indicadores do período selecionado") +
	        "</p></div></div>";

	    [row1, row2, row3].forEach(function (row) {
	        h += '<div class="painel-kpi-row">';
	        row.forEach(function (item) {
	            var cls = "painel-kpi";
	            if (item.urgent) cls += " urgent";
	            if (item.positive) cls += " positive";
	            if (item.warn) cls += " warn";
	            h +=
	                '<div class="' +
	                cls +
	                '" data-kpi-route="' +
	                (item.route || "") +
	                '">' +
	                '<div class="painel-kpi-label">' +
	                item.label +
	                "</div>" +
	                '<div class="painel-kpi-value">' +
	                item.value +
	                "</div></div>";
	        });
	        h += "</div>";
	    });
	    h += "</section>";
	    return h;
	}

})(advocacia.painel.kpis = advocacia.painel.kpis || {});
