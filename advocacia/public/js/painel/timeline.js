/* eslint-disable */
frappe.provide("advocacia.painel.timeline");
(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.render_timeline = function(timeline, periodo_dias, list_meta, list_limit) {
	    periodo_dias = U.cint(periodo_dias) || 7;
	    var titulo =
	        periodo_dias === 1
	            ? __("Agenda de hoje")
	            : __("Agenda — próximos {0} dias", [periodo_dias]);
	    var subtitle =
	        periodo_dias === 1
	            ? __("Audiências, prazos e tarefas de hoje")
	            : __("Audiências, prazos e tarefas {0}", [U.painel_periodo_enunciado(periodo_dias)]);
	    var meta_html = U.painel_list_meta_html(list_meta, list_limit);
	    var h =
	        '<section class="painel-section painel-section--timeline painel-priority-high" id="painel-timeline"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        titulo +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        subtitle +
	        "</p></div>" +
	        '<div class="painel-section-head-actions">' +
	        U.render_list_limit_controls("timeline", list_limit) +
	        meta_html +
	        '<span class="painel-section-link" data-route-calendar="1">' +
	        __("Ver agenda") +
	        "</span></div></div>";

	    if (!timeline || !timeline.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_empty_state(
	                "calendar",
	                __("Agenda tranquila"),
	                periodo_dias === 1
	                    ? __("Nada agendado para hoje.")
	                    : __("Nenhum compromisso no período selecionado.")
	            ) +
	            "</div></section>"
	        );
	    }

	    h += '<div class="painel-panel"><div class="painel-timeline-modern">';
	    timeline.forEach(function (it) {
	        var tipo_label =
	            it.type === "audiencia"
	                ? __("Audiência")
	                : it.type === "prazo"
	                  ? __("Prazo")
	                  : __("Legal Task");
	        var tipo_icon =
	            it.type === "audiencia" ? "milestone" : it.type === "prazo" ? "time" : "checklist";
	        var pill_map = {
	            red: "Alta",
	            orange: "Média",
	            yellow: "Normal",
	            blue: "Normal",
	            gray: "Baixa",
	        };
	        var tone = it.urgencia || "blue";
	        var dias =
	            it.dias_restantes != null ? it.dias_restantes : U.painel_day_diff(it.date);
	        var when = U.painel_timeline_when_label(it.date, it.hora, dias);
	        h +=
	            '<div class="painel-tl-item tone-' +
	            tone +
	            '" data-dt="' +
	            frappe.utils.escape_html(it.doctype || "") +
	            '" data-dn="' +
	            frappe.utils.escape_html(it.docname || "") +
	            '">' +
	            '<span class="painel-tl-marker" aria-hidden="true"></span>' +
	            '<div class="painel-tl-content">' +
	            '<div class="painel-tl-when">' +
	            frappe.utils.escape_html(when) +
	            "</div>" +
	            '<div class="painel-tl-type">' +
	            U.painel_icon(tipo_icon) +
	            frappe.utils.escape_html(tipo_label) +
	            "</div>" +
	            '<div class="painel-tl-title">' +
	            frappe.utils.escape_html(it.title || "") +
	            "</div>" +
	            '<div class="painel-tl-sub">' +
	            frappe.utils.escape_html(it.subtitle || "") +
	            (it.detalhe ? " · " + frappe.utils.escape_html(it.detalhe) : "") +
	            "</div></div>" +
	            U.status_pill(pill_map[tone] || "Normal") +
	            "</div>";
	    });
	    h += "</div></div></section>";
	    return h;
	}

	AP.build_timeline_items = function(d) {
	    var items = [];
	    (d.alertas || []).forEach(function (a) {
	        items.push({
	            sort: a.type === "prazo" && a.dias <= 0 ? 0 : 1,
	            time: a.hora || (a.type === "prazo" ? __("Prazo") : __("Hoje")),
	            title: a.title,
	            sub:
	                ((a.client_nome || a.client) ? (a.client_nome || a.client) + " · " : "") +
	                (a.type === "prazo"
	                    ? a.dias === 0
	                        ? __("Vence hoje")
	                        : __("Amanhã")
	                    : __("Audiência")),
	            doctype: a.doctype,
	            docname: a.docname,
	            pill: a.nivel === "red" ? "red" : "orange",
	        });
	    });
	    (d.audiencias || []).forEach(function (a) {
	        if (a.dias_restantes !== 0) return;
	        items.push({
	            sort: 2,
	            time: a.hora || __("—"),
	            title: a.type || __("Audiência"),
	            sub: ((a.client_nome || a.client) || "") + (a.court_branch_link_label ? " · " + a.court_branch_link_label : ""),
	            doctype: "Hearing",
	            docname: a.name,
	            pill: "blue",
	        });
	    });
	    (d.prazos || []).forEach(function (p) {
	        if (p.dias_restantes > 1) return;
	        items.push({
	            sort: p.dias_restantes <= 0 ? 0 : 1,
	            time: U.fmt_date_iso(p.due_date),
	            title: p.description || p.name,
	            sub: p.client_nome || "",
	            doctype: "Deadline",
	            docname: p.name,
	            pill: p.dias_restantes <= 0 ? "red" : "orange",
	        });
	    });
	    items.sort(function (a, b) {
	        return a.sort - b.sort;
	    });
	    if (!items.length) return "";
	    return items
	        .map(function (it) {
	            var hot = it.sort <= 1 ? " painel-op-item--hot" : "";
	            return (
	                '<div class="painel-op-item' +
	                hot +
	                '" data-dt="' +
	                it.doctype +
	                '" data-dn="' +
	                frappe.utils.escape_html(it.docname) +
	                '">' +
	                '<div class="painel-op-time">' +
	                frappe.utils.escape_html(String(it.time)) +
	                "</div>" +
	                '<div class="painel-op-body"><div class="painel-op-title">' +
	                frappe.utils.escape_html(it.title) +
	                '</div><div class="painel-op-sub">' +
	                frappe.utils.escape_html(it.sub) +
	                "</div></div>" +
	                '<div class="painel-op-side">' +
	                U.status_pill(it.pill === "red" ? "Alta" : it.pill === "orange" ? "Média" : "Normal") +
	                "</div></div>"
	            );
	        })
	        .join("");
	}

	AP.render_comunicacoes_pendentes = function(comunicacoes, periodo_dias, list_meta, list_limit) {
	    periodo_dias = U.cint(periodo_dias) || 7;
	    var meta_html = U.painel_list_meta_html(list_meta, list_limit);
	    var h =
	        '<section class="painel-section painel-priority-high" id="painel-comunicacoes"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Comunicações") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Follow-ups pendentes — visão {0}", [U.painel_periodo_enunciado(periodo_dias)]) +
	        "</p></div>" +
	        '<div class="painel-section-head-actions">' +
	        U.render_list_limit_controls("comunicacoes", list_limit) +
	        meta_html +
	        '<span class="painel-section-link" data-route-list="Case Communication">' +
	        __("Ver todas") +
	        "</span></div></div>";

	    if (!comunicacoes || !comunicacoes.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_success_state(
	                __("Nenhuma comunicação pendente"),
	                __("Retornos e follow-ups aparecerão aqui quando precisarem de ação.")
	            ) +
	            "</div></section>"
	        );
	    }

	    h += '<div class="painel-panel"><div class="painel-schedule-list">';
	    comunicacoes.forEach(function (c) {
	        var urg = c.urgencia_ordem === 0 ? "red" : c.urgencia_ordem === 1 ? "orange" : "yellow";
	        var status_label = urg === "red" ? __("Alta") : urg === "orange" ? __("Média") : __("Normal");
	        h +=
	            '<div class="painel-com-item" data-comunicacao="' +
	            frappe.utils.escape_html(c.name || "") +
	            '" data-dt="Case Communication" data-dn="' +
	            frappe.utils.escape_html(c.name || "") +
	            '">' +
	            '<div class="painel-com-main">' +
	            '<div class="painel-com-cliente">' +
	            frappe.utils.escape_html(c.client_nome || c.client || __("Sem cliente")) +
	            "</div>" +
	            '<div class="painel-com-assunto">' +
	            frappe.utils.escape_html(c.subject || c.name) +
	            "</div>" +
	            (c.motivo_pendencia
	                ? '<div class="painel-com-meta">' +
	                  frappe.utils.escape_html(c.motivo_pendencia) +
	                  "</div>"
	                : "") +
	            "</div>" +
	            '<div class="painel-com-side">' +
	            U.status_pill(status_label) +
	            '<span class="painel-com-dias">' +
	            __("{0}d sem retorno", [c.dias_sem_retorno || 0]) +
	            "</span></div></div>";
	    });
	    h += "</div></div></section>";
	    return h;
	}

	AP.render_comunicacoes = function(comunicacoes) {
	    var h =
	        '<section class="painel-section" id="painel-comunicacoes"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Últimas Comunicações") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Interações recentes com clientes") +
	        "</p></div>" +
	        '<span class="painel-section-link" data-route-list="Case Communication">' +
	        __("Ver todas") +
	        "</span></div>";

	    if (!comunicacoes || !comunicacoes.length) {
	        return (
	            h +
	            '<div class="painel-panel">' +
	            U.render_empty_state(
	                "message",
	                __("Nenhuma comunicação registrada"),
	                __("Ligações, e-mails e reuniões aparecerão aqui.")
	            ) +
	            "</div></section>"
	        );
	    }

	    h += '<div class="painel-panel"><div class="painel-schedule-list">';
	    comunicacoes.forEach(function (c) {
	        h +=
	            '<div class="painel-schedule-item" data-dt="Case Communication" data-dn="' +
	            frappe.utils.escape_html(c.name || "") +
	            '">' +
	            '<div class="painel-schedule-main">' +
	            '<div class="painel-op-title">' +
	            frappe.utils.escape_html(c.subject || c.name) +
	            "</div>" +
	            '<div class="painel-op-sub">' +
	            frappe.utils.escape_html(c.type || "") +
	            ((c.client_nome || c.client) ? " · " + frappe.utils.escape_html(c.client_nome || c.client) : "") +
	            "</div></div>" +
	            '<div class="painel-schedule-side">' +
	            (c.communication_date
	                ? '<span class="painel-op-sub">' +
	                  frappe.utils.escape_html(frappe.datetime.str_to_user(c.communication_date)) +
	                  "</span>"
	                : "") +
	            "</div></div>";
	    });
	    h += "</div></div></section>";
	    return h;
	}

	AP.render_prazo_items = function(prazos) {
	    if (!prazos || !prazos.length) return "";
	    return prazos
	        .map(function (p) {
	            var dias = p.dias_restantes;
	            var cd = U.prazo_countdown_label(dias);
	            var parts = U.painel_date_parts(p.due_date);
	            var card_cls = "painel-schedule-card";
	            if (dias < 0) card_cls += " painel-schedule-card--urgent";
	            else if (dias <= 1) card_cls += " painel-schedule-card--today";
	            return (
	                '<div class="' +
	                card_cls +
	                '" data-dt="Deadline" data-dn="' +
	                frappe.utils.escape_html(p.name) +
	                '">' +
	                '<div class="painel-schedule-when">' +
	                '<span class="painel-schedule-day">' +
	                frappe.utils.escape_html(parts.day) +
	                "</span>" +
	                '<span class="painel-schedule-month">' +
	                frappe.utils.escape_html(parts.month) +
	                "</span>" +
	                '<span class="painel-schedule-countdown ' +
	                cd.cls +
	                '">' +
	                frappe.utils.escape_html(cd.text) +
	                "</span></div>" +
	                '<div class="painel-schedule-body">' +
	                '<div class="painel-schedule-title">' +
	                frappe.utils.escape_html(p.description || p.name) +
	                "</div>" +
	                '<div class="painel-schedule-sub">' +
	                frappe.utils.escape_html(p.client_nome || "—") +
	                (p.legal_case_titulo ? " · " + frappe.utils.escape_html(p.legal_case_titulo) : "") +
	                "</div></div>" +
	                '<div class="painel-schedule-meta">' +
	                U.status_pill(p.priority || "Normal") +
	                "</div></div>"
	            );
	        })
	        .join("");
	}

	AP.render_tarefa_items = function(tarefas) {
	    if (!tarefas || !tarefas.length) return "";
	    return tarefas
	        .map(function (t) {
	            var parts = U.painel_date_parts(t.due_date);
	            var cd = t.due_date
	                ? U.prazo_countdown_label(t.dias_restantes != null ? t.dias_restantes : 99)
	                : { text: __("Sem prazo"), cls: "" };
	            var card_cls = "painel-schedule-card";
	            if (t.dias_restantes != null && t.dias_restantes < 0) {
	                card_cls += " painel-schedule-card--urgent";
	            } else if (t.dias_restantes === 0) {
	                card_cls += " painel-schedule-card--today";
	            }
	            return (
	                '<div class="' +
	                card_cls +
	                '" data-dt="Legal Task" data-dn="' +
	                frappe.utils.escape_html(t.name) +
	                '">' +
	                '<div class="painel-schedule-when">' +
	                (t.due_date
	                    ? '<span class="painel-schedule-day">' +
	                      frappe.utils.escape_html(parts.day) +
	                      "</span>" +
	                      '<span class="painel-schedule-month">' +
	                      frappe.utils.escape_html(parts.month) +
	                      "</span>"
	                    : '<span class="painel-schedule-day">—</span>') +
	                '<span class="painel-schedule-countdown ' +
	                cd.cls +
	                '">' +
	                frappe.utils.escape_html(cd.text) +
	                "</span></div>" +
	                '<div class="painel-schedule-body">' +
	                '<div class="painel-schedule-title">' +
	                frappe.utils.escape_html(t.subject || "") +
	                "</div>" +
	                '<div class="painel-schedule-sub">' +
	                frappe.utils.escape_html(t.responsavel_nome || "—") +
	                (t.client_nome ? " · " + frappe.utils.escape_html(t.client_nome) : "") +
	                "</div></div>" +
	                '<div class="painel-schedule-meta">' +
	                U.status_pill(t.status) +
	                "</div></div>"
	            );
	        })
	        .join("");
	}

	AP.render_operacao_dia = function(d) {
	    var timeline = T.build_timeline_items(d);
	    var criticas = F.build_parcelas_criticas(d.fee_installments, 5);
	    var h =
	        '<section class="painel-section painel-section--primary"><div class="painel-section-head">' +
	        "<div><h2 class='painel-section-title'>" +
	        __("Operação do dia") +
	        "</h2>" +
	        '<p class="painel-section-sub">' +
	        __("Central de urgências, agenda e cobrança imediata") +
	        "</p></div></div>" +
	        '<div class="painel-operacao-grid">';
	    h +=
	        '<div class="painel-panel"><div class="painel-panel-head">' +
	        __("Agenda e urgências") +
	        "</div>" +
	        '<div class="painel-op-list">' +
	        (timeline ||
	            U.render_empty_state(
	                "calendar",
	                __("Agenda tranquila hoje"),
	                __("Sem prazos ou audiências críticos para as próximas horas.")
	            )) +
	        "</div></div>";
	    h +=
	        '<div class="painel-panel" id="painel-parcelas-criticas"><div class="painel-panel-head">' +
	        __("Parcelas críticas") +
	        "</div>" +
	        '<div class="painel-op-list">' +
	        (criticas ||
	            U.render_empty_state(
	                "money",
	                __("Nenhuma parcela vencida"),
	                __("Honorários em dia — excelente controle de recebíveis.")
	            )) +
	        "</div></div>";
	    h += "</div></section>";
	    return h;
	}

})(advocacia.painel.timeline = advocacia.painel.timeline || {});
