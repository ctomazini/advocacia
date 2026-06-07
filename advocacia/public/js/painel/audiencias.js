/* eslint-disable */
frappe.provide("advocacia.painel.audiencias");
(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var A = advocacia.painel.audiencias;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.painel_find_proximas_audiencias = function(audiencias, timeline, limit) {
	    limit = U.cint(limit) || 2;
	    if (audiencias && audiencias.length) {
	        return audiencias.slice(0, limit);
	    }
	    var found = [];
	    if (timeline && timeline.length) {
	        for (var i = 0; i < timeline.length && found.length < limit; i++) {
	            if (timeline[i].tipo !== "audiencia") continue;
	            found.push({
	                name: timeline[i].docname,
	                tipo: timeline[i].titulo,
	                cliente: timeline[i].subtitulo,
	                servico: timeline[i].detalhe,
	                data: timeline[i].data,
	                hora: timeline[i].hora,
	                dias_restantes: U.painel_day_diff(timeline[i].data),
	                vara_label: timeline[i].detalhe,
	                modalidade: "Presencial",
	                link_virtual: "",
	            });
	        }
	    }
	    return found;
	}

	AP.painel_audiencia_modalidade_html = function(a) {
	    var mod = a.modalidade || "Presencial";
	    var icon = mod === "Virtual" ? "video" : mod === "Híbrida" ? "monitor" : "map-pin";
	    var cls =
	        mod === "Virtual" ? "virtual" : mod === "Híbrida" ? "hibrida" : "presencial";
	    return (
	        '<span class="painel-prox-mod painel-prox-mod--' +
	        cls +
	        '">' +
	        U.painel_icon(icon) +
	        frappe.utils.escape_html(mod) +
	        "</span>"
	    );
	}

	AP.painel_audiencia_entrar_html = function(a) {
	    var mod = a.modalidade || "Presencial";
	    if (mod !== "Virtual" && mod !== "Híbrida") {
	        return "";
	    }
	    if (a.link_virtual) {
	        return (
	            '<a class="painel-btn-entrar" href="' +
	            frappe.utils.escape_html(a.link_virtual) +
	            '" target="_blank" rel="noopener" onclick="event.stopPropagation();">' +
	            U.painel_icon("external-link") +
	            "<span>" +
	            __("Entrar na audiência") +
	            "</span></a>"
	        );
	    }
	    return (
	        '<span class="painel-btn-entrar painel-btn-entrar--muted" title="' +
	        frappe.utils.escape_html(__("Link ainda não cadastrado")) +
	        '">' +
	        __("Sem link") +
	        "</span>"
	    );
	}

	AP.render_proxima_audiencia_card = function(a, ordem) {
	    var when = U.painel_timeline_when_label(a.data, a.hora, a.dias_restantes);
	    var mod = a.modalidade || "Presencial";
	    var local =
	        a.court_branch_link_label ||
	        (mod === "Presencial" || mod === "Híbrida" ? a.court_branch || "" : "");
	    var entrar = A.painel_audiencia_entrar_html(a);
	    var h =
	        '<div class="painel-prox-card" data-dt="Hearing" data-dn="' +
	        frappe.utils.escape_html(a.name || "") +
	        '">' +
	        '<div class="painel-prox-card-head">' +
	        '<div class="painel-prox-when">' +
	        (ordem
	            ? '<span class="painel-prox-ordem">' +
	              frappe.utils.escape_html(__("#{0}", [ordem])) +
	              " · " +
	              "</span>"
	            : "") +
	        frappe.utils.escape_html(when) +
	        "</div>" +
	        A.painel_audiencia_modalidade_html(a) +
	        "</div>" +
	        '<div class="painel-prox-tipo">' +
	        frappe.utils.escape_html(a.tipo || __("Audiência")) +
	        "</div>" +
	        '<div class="painel-prox-meta">' +
	        '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
	        __("Client") +
	        '</span><span class="painel-prox-row-value">' +
	        frappe.utils.escape_html(a.client_nome || a.client || "—") +
	        "</span></div>" +
	        '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
	        __("Serviço") +
	        '</span><span class="painel-prox-row-value">' +
	        frappe.utils.escape_html(a.legal_case_titulo || a.legal_case || "—") +
	        "</span></div>";
	    if (local && mod !== "Virtual") {
	        h +=
	            '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
	            __("Local") +
	            '</span><span class="painel-prox-row-value">' +
	            frappe.utils.escape_html(local) +
	            "</span></div>";
	    }
	    h += "</div>";
	    if (entrar) {
	        h += '<div class="painel-prox-actions">' + entrar + "</div>";
	    }
	    h += "</div>";
	    return h;
	}

	AP.render_proxima_audiencia = function(audiencias, timeline) {
	    var items = A.painel_find_proximas_audiencias(audiencias, timeline, 2);
	    var h =
	        '<div class="painel-prox-audiencia painel-priority-max" id="painel-prox-audiencia">' +
	        '<div class="painel-prox-audiencia-head">' +
	        '<span class="painel-prox-badge">' +
	        U.painel_icon("calendar-days") +
	        "</span>" +
	        '<h3 class="painel-prox-title">' +
	        __("Próximas Audiências") +
	        "</h3></div>";

	    if (!items.length) {
	        return (
	            h +
	            '<div class="painel-prox-empty">' +
	            __("Nenhuma audiência agendada.") +
	            "</div></div>"
	        );
	    }

	    h += '<div class="painel-prox-list">';
	    items.forEach(function (a, idx) {
	        h += A.render_proxima_audiencia_card(a, idx + 1);
	    });
	    h += "</div></div>";
	    return h;
	}

	AP.render_audiencia_items = function(audiencias) {
	    if (!audiencias || !audiencias.length) return "";
	    return audiencias
	        .map(function (a) {
	            var parts = U.painel_date_parts(a.data);
	            var card_cls = "painel-schedule-card";
	            if (a.dias_restantes === 0) card_cls += " painel-schedule-card--today";
	            var btn = "";
	            if (a.modalidade === "Virtual") {
	                if (a.link_virtual) {
	                    btn =
	                        '<a class="painel-btn-entrar" href="' +
	                        frappe.utils.escape_html(a.link_virtual) +
	                        '" target="_blank" rel="noopener" onclick="event.stopPropagation();">' +
	                        __("Entrar") +
	                        "</a>";
	                } else {
	                    btn =
	                        '<span class="painel-btn-entrar painel-btn-entrar--muted" title="' +
	                        frappe.utils.escape_html(__("Link ainda não cadastrado")) +
	                        '">' +
	                        __("Sem link") +
	                        "</span>";
	                }
	            }
	            return (
	                '<div class="' +
	                card_cls +
	                '" data-dt="Hearing" data-dn="' +
	                frappe.utils.escape_html(a.name) +
	                '">' +
	                '<div class="painel-schedule-when">' +
	                '<span class="painel-schedule-day">' +
	                frappe.utils.escape_html(parts.day) +
	                "</span>" +
	                '<span class="painel-schedule-month">' +
	                frappe.utils.escape_html(parts.month) +
	                "</span>" +
	                (a.hora
	                    ? '<span class="painel-schedule-hour">' + frappe.utils.escape_html(a.hora) + "</span>"
	                    : "") +
	                "</div>" +
	                '<div class="painel-schedule-body">' +
	                '<div class="painel-schedule-title">' +
	                frappe.utils.escape_html(a.client_nome || a.client || "—") +
	                "</div>" +
	                '<div class="painel-schedule-sub">' +
	                frappe.utils.escape_html(a.tipo || __("Audiência")) +
	                (a.court_branch_link_label ? " · " + frappe.utils.escape_html(a.court_branch_link_label) : "") +
	                "</div></div>" +
	                '<div class="painel-schedule-meta">' +
	                U.status_pill(a.modalidade || "Presencial") +
	                btn +
	                "</div></div>"
	            );
	        })
	        .join("");
	}

})(advocacia.painel.audiencias = advocacia.painel.audiencias || {});
