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

	AP.painel_is_onboarding = function(d) {
	    var meta = (d && d.list_meta) || {};
	    var active = meta.active_cases || {};
	    return (active.total || 0) === 0;
	}

	AP.render_header_onboarding = function() {
	    return (
	        '<header class="painel-hero painel-hero--onboarding" id="painel-hero">' +
	        '<h1 class="painel-hero-greeting">' +
	        H.painel_greeting() +
	        "</h1>" +
	        '<p class="painel-hero-date">' +
	        frappe.utils.escape_html(frappe.datetime.get_today(true)) +
	        "</p>" +
	        '<p class="painel-hero-context">' +
	        frappe.utils.escape_html(
	            __("Bem-vindo ao escritório. Siga os passos abaixo para começar.")
	        ) +
	        "</p></header>"
	    );
	}

	AP.render_onboarding_journey = function() {
	    var steps = [
	        {
	            n: 1,
	            title: __("Cadastrar um Cliente"),
	            hint: __("Quem você representa — pessoa física ou jurídica."),
	            dt: "Client",
	            chip: __("Cliente"),
	        },
	        {
	            n: 2,
	            title: __("Cadastrar um Processo"),
	            hint: __("Processo judicial, consultoria ou outro serviço vinculado ao cliente."),
	            dt: "Legal Case",
	            chip: __("Processo"),
	        },
	        {
	            n: 3,
	            title: __("Acessar o processo e configurar"),
	            hint: __("No hub do processo: prazos, audiências e honorários."),
	            list_dt: "Legal Case",
	            chip: __("Ver processos"),
	        },
	    ];
	    var h =
	        '<section class="painel-onboarding" id="painel-onboarding">' +
	        U.render_empty_state(
	            "rocket",
	            __("Primeiros passos"),
	            __("Configure o escritório em três etapas.")
	        );
	    h += '<ol class="painel-onboarding-steps">';
	    steps.forEach(function (step) {
	        h +=
	            '<li class="painel-onboarding-step">' +
	            '<span class="painel-onboarding-step__n">' +
	            step.n +
	            "</span>" +
	            '<div class="painel-onboarding-step__body">' +
	            '<p class="painel-onboarding-step__title">' +
	            frappe.utils.escape_html(step.title) +
	            "</p>" +
	            '<p class="painel-onboarding-step__hint">' +
	            frappe.utils.escape_html(step.hint) +
	            "</p>";
	        if (step.dt) {
	            h +=
	                '<button type="button" class="painel-action-chip painel-onboarding-step__cta" data-new-dt="' +
	                step.dt +
	                '">' +
	                U.painel_icon("plus") +
	                "<span>+ " +
	                frappe.utils.escape_html(step.chip) +
	                "</span></button>";
	        } else if (step.list_dt) {
	            h +=
	                '<button type="button" class="painel-action-chip painel-onboarding-step__cta" data-route-list="' +
	                step.list_dt +
	                '">' +
	                U.painel_icon("arrow-right") +
	                "<span>" +
	                frappe.utils.escape_html(step.chip) +
	                "</span></button>";
	        }
	        h += "</div></li>";
	    });
	    h += "</ol></section>";
	    return h;
	}

	AP.render_financial_restricted = function() {
	    return (
	        '<div class="painel-zona-financeira painel-zona-secundaria painel-zona-financeira--restricted">' +
	        '<div class="painel-zona-financeira__head">' +
	        "<div><h2 class=\"painel-section-title\">" +
	        __("Financeiro") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Indicadores e recebimentos do escritório") +
	        "</p></div></div>" +
	        U.render_empty_state(
	            "lock",
	            __("Dados financeiros restritos"),
	            __(
	                "Parcelas, recebimentos e indicadores financeiros são visíveis apenas para o perfil Gestor (Advocacia Manager). Solicite acesso ao administrador do sistema."
	            )
	        ) +
	        "</div>"
	    );
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

	AP.render_acoes_rapidas = function(onboarding) {
	    var actions = [
	        { label: __("Cliente"), icon: "user-plus", dt: "Client" },
	        { label: __("Processo"), icon: "folder-plus", dt: "Legal Case" },
	        { label: __("Audiência"), icon: "calendar-plus-2", dt: "Hearing" },
	        { label: __("Prazo"), icon: "clock-plus", dt: "Deadline" },
	        { label: __("Comunicação"), icon: "message-square-plus", dt: "Case Communication" },
	        { label: __("Tarefa"), icon: "list-plus", dt: "Legal Task" },
	        { label: __("Honorário"), icon: "file-plus", dt: "Fee Agreement" },
	        { label: __("Recebimento"), icon: "circle-dollar-sign", dt: "Legal Payment" },
	        { label: __("Custa"), icon: "receipt", dt: "Court Cost" },
	        { label: __("Horas"), icon: "clock", dt: "Time Entry" },
	        { label: __("Despesa do Escritório"), icon: "wallet", dt: "Office Expense" },
	    ];
	    var onboarding_dts = ["Client", "Legal Case", "Deadline", "Hearing"];
	    if (onboarding) {
	        actions = actions.filter(function (a) {
	            return onboarding_dts.indexOf(a.dt) >= 0;
	        });
	    }
	    var h =
	        '<div class="painel-actions-wrap">' +
	        '<p class="painel-actions-label">' +
	        (onboarding ? __("Comece por aqui") : __("Ações rápidas")) +
	        "</p>" +
	        '<div class="painel-actions">';
	    actions.forEach(function (a) {
	        h +=
	            '<button type="button" class="painel-action-chip" data-new-dt="' +
	            a.dt +
	            '">' +
	            U.painel_icon(a.icon) +
	            "<span>+ " +
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
