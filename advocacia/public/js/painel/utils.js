/* eslint-disable */
frappe.provide("advocacia");
frappe.provide("advocacia.painel.utils");
(function (U) {
	var PAINEL_LIST_LIMIT_KEYS = [
	    "timeline",
	    "comunicacoes",
	    "fee_installments",
	    "despesas",
	    "custas",
	];
	

	U.cint = function(val) {
	    return parseInt(val, 10) || 0;
	}

	U.flt = function(val) {
	    return parseFloat(val) || 0;
	}

	U.painel_icon = function(name) {
	    try {
	        return frappe.utils.icon(name, "sm") || "";
	    } catch (e) {
	        return "";
	    }
	}

	U.fmt_currency = function(val, plain) {
	    if (plain) {
	        return format_currency(val || 0, "BRL");
	    }
	    return frappe.format(val || 0, { fieldtype: "Currency", currency: "BRL" });
	}

	U.fmt_date_iso = function(iso) {
	    if (!iso) return "";
	    return frappe.datetime.str_to_user(iso);
	}

	U.fmt_datetime = function(iso, hora) {
	    if (!iso) return "";
	    var s = U.fmt_date_iso(iso);
	    if (hora) s += " " + hora;
	    return s;
	}

	U._is_vencido = function(status) {
	    return status === "Vencido";
	}

	U._pagamento_pode_receber = function(status) {
	    return status === "Pendente" || U._is_vencido(status);
	}

	U.status_pill = function(status) {
	    var map = {
	        Vencido: "red",
	        Pendente: "orange",
	        Recebido: "green",
	        Repassado: "blue",
	        Cancelado: "gray",
	        Cancelada: "gray",
	        "Em Andamento": "blue",
	        Concluída: "green",
	        Alta: "red",
	        "Média": "orange",
	        Media: "orange",
	        Virtual: "blue",
	        Presencial: "gray",
	        Híbrida: "orange",
	        Normal: "gray",
	        Baixa: "gray",
	    };
	    var cls = map[status] || "gray";
	    return (
	        '<span class="indicator-pill ' +
	        cls +
	        ' filterable no-indicator-dot ellipsis">' +
	        frappe.utils.escape_html(status || "") +
	        "</span>"
	    );
	}

	U.scroll_painel_section = function(id) {
	    var el = document.getElementById(id);
	    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
	}

	U.painel_default_list_limits = function() {
	    return {
	        timeline: 5,
	        comunicacoes: 5,
	        parcelas: 5,
	        despesas: 5,
	        custas: 5,
	    };
	}

	U.painel_merge_list_limits = function(page) {
	    var defaults = U.painel_default_list_limits();
	    var current = (page && page.painel_list_limits) || {};
	    var merged = {};
	    PAINEL_LIST_LIMIT_KEYS.forEach(function (key) {
	        merged[key] = current[key] != null ? U.cint(current[key]) : defaults[key];
	    });
	    return merged;
	}

	U.render_list_limit_controls = function(list_key, current_limit) {
	    var opcoes = [
	        { val: 5, label: "5" },
	        { val: 10, label: "10" },
	        { val: 15, label: "15" },
	        { val: 0, label: __("Todos") },
	    ];
	    current_limit = current_limit != null ? U.cint(current_limit) : 5;
	    var h =
	        '<div class="painel-linhas-filters painel-linhas-filters--inline" title="' +
	        __("Itens nesta lista") +
	        '">';
	    opcoes.forEach(function (op) {
	        h +=
	            '<button type="button" class="painel-linhas-btn' +
	            (current_limit === op.val ? " active" : "") +
	            '" data-list="' +
	            list_key +
	            '" data-linhas="' +
	            op.val +
	            '">' +
	            op.label +
	            "</button>";
	    });
	    h += "</div>";
	    return h;
	}

	U.painel_periodo_fim = function(page) {
	    var dias = (page && page.painel_periodo) || 7;
	    return frappe.datetime.add_days(frappe.datetime.get_today(), dias);
	}

	U.painel_periodo_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("hoje");
	    if (dias === 7) return __("7 dias");
	    if (dias === 15) return __("15 dias");
	    if (dias === 30) return __("30 dias");
	    return __("{0} dias", [dias]);
	}

	U.painel_periodo_previsto_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("previsto hoje");
	    if (dias === 7) return __("previsto em 7 dias");
	    if (dias === 15) return __("previsto em 15 dias");
	    if (dias === 30) return __("previsto em 30 dias");
	    return __("previsto em {0} dias", [dias]);
	}

	U.painel_periodo_a_receber_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("A receber hoje");
	    return __("A receber ({0})", [U.painel_periodo_label(dias)]);
	}

	U.painel_periodo_recebidos_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("Recebidos hoje");
	    return __("Recebidos ({0})", [U.painel_periodo_label(dias)]);
	}

	U.painel_periodo_enunciado = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("hoje");
	    return __("nos próximos {0} dias", [dias]);
	}

	U.painel_periodo_scope_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("Período: hoje");
	    return __("Período: {0} dias", [dias]);
	}

	U.painel_horas_label = function(dias) {
	    dias = U.cint(dias) || 7;
	    if (dias === 1) return __("Horas hoje");
	    return __("Horas ({0})", [U.painel_periodo_label(dias)]);
	}

	U.painel_list_meta_html = function(meta, list_limit) {
	    if (!meta || !meta.total) return "";
	    if (!list_limit || list_limit === 0 || meta.showing >= meta.total) {
	        return (
	            '<span class="painel-list-meta">' +
	            __("Todos ({0})", [meta.total]) +
	            "</span>"
	        );
	    }
	    return (
	        '<span class="painel-list-meta">' +
	        __("{0} de {1}", [meta.showing, meta.total]) +
	        "</span>"
	    );
	}

	U.painel_goto_list = function(doctype, filters) {
	    advocacia.list_nav.goto(doctype, filters || []);
	}

	U.render_success_state = function(title, hint) {
	    return (
	        '<div class="painel-success-state">' +
	        '<div class="painel-success-icon">' +
	        U.painel_icon("check-circle") +
	        "</div>" +
	        '<p class="painel-success-title">' +
	        frappe.utils.escape_html(title) +
	        "</p>" +
	        (hint
	            ? '<p class="painel-success-hint">' + frappe.utils.escape_html(hint) + "</p>"
	            : "") +
	        "</div>"
	    );
	}

	U.render_empty_state = function(icon, title, hint) {
	    return (
	        '<div class="painel-empty">' +
	        '<div class="painel-empty-icon">' +
	        U.painel_icon(icon || "inbox") +
	        "</div>" +
	        '<p class="painel-empty-title">' +
	        frappe.utils.escape_html(title) +
	        "</p>" +
	        (hint
	            ? '<p class="painel-empty-hint">' + frappe.utils.escape_html(hint) + "</p>"
	            : "") +
	        "</div>"
	    );
	}

	U.painel_date_parts = function(iso) {
	    if (!iso) {
	        return { day: "—", month: "" };
	    }
	    var months = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
	    var d = frappe.datetime.str_to_obj(iso);
	    return {
	        day: String(d.getDate()).padStart(2, "0"),
	        month: months[d.getMonth()] || "",
	    };
	}

	U.prazo_countdown_label = function(dias) {
	    if (dias < 0) {
	        return { text: __("Vencido"), cls: "danger" };
	    }
	    if (dias === 0) {
	        return { text: __("Hoje"), cls: "warn" };
	    }
	    if (dias === 1) {
	        return { text: __("Amanhã"), cls: "warn" };
	    }
	    return { text: __("Em {0}d", [dias]), cls: "" };
	}

	U.painel_day_diff = function(date_str) {
	    if (!date_str) return null;
	    return frappe.datetime.get_day_diff(date_str, frappe.datetime.get_today());
	}

	U.painel_timeline_when_label = function(data, hora, dias_restantes) {
	    if (dias_restantes == null && data) {
	        dias_restantes = U.painel_day_diff(data);
	    }
	    if (dias_restantes === 0) {
	        return hora ? __("Hoje {0}", [hora]) : __("Hoje");
	    }
	    if (dias_restantes === 1) {
	        return hora ? __("Amanhã {0}", [hora]) : __("Amanhã");
	    }
	    var base = U.fmt_date_iso(data);
	    return hora ? base + " · " + hora : base;
	}

	U.painel_polish_frappe_chrome = function() {
	    $(document.body).addClass("advocacia-painel-active");
	}

})(advocacia.painel.utils = advocacia.painel.utils || {});
