/* eslint-disable */
frappe.provide("advocacia.painel");

advocacia.painel.init = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Painel do Escritório"),
		single_column: true,
	});

	page.painel_container = $('<div class="painel-root"></div>').appendTo(page.main);
	advocacia.painel.utils.painel_polish_frappe_chrome();

	page.add_button(__("↺ Atualizar"), function () {
		advocacia.painel.load(page);
	});

	frappe.pages.painel.page = page;
	page.painel_periodo = 7;
	page.painel_list_limits = advocacia.painel.utils.painel_default_list_limits();
	advocacia.painel.bind_painel_filters(page.painel_container, page);
	advocacia.painel.bind_atencao_routes(page.painel_container, page);
	advocacia.painel.load(page);
};

(function (AP) {
	var U = advocacia.painel.utils;
	var H = advocacia.painel.hero;
	var K = advocacia.painel.kpis;
	var A = advocacia.painel.audiencias;
	var T = advocacia.painel.timeline;
	var F = advocacia.painel.financeiro;

	AP.mostrar_skeleton = function($container) {
	    var html =
	        '<div class="painel-skeleton-hero"></div>' +
	        '<div class="painel-skeleton-kpis">' +
	        '<div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div>' +
	        "</div>" +
	        '<div class="painel-skeleton-panel"></div><div class="painel-skeleton-panel"></div>';
	    $container.html(html);
	}

	AP.handle_error = function($container, err) {
	    var msg = (err && err.message) || String(err);
	    $container.html(
	        '<div class="painel-panel"><div class="painel-empty" style="color: var(--red-500);">' +
	            __("Erro ao carregar o painel: {0}", [msg]) +
	            "</div></div>"
	    );
	}

	AP._scroll_parent = function(page) {
	    var el = page.painel_container[0];
	    while (el && el !== document.body) {
	        if (el.scrollHeight > el.clientHeight + 1) {
	            return $(el);
	        }
	        el = el.parentElement;
	    }
	    return $(window);
	}

	AP._save_scroll = function(page) {
	    var $sp = AP._scroll_parent(page);
	    return { $el: $sp, top: $sp.scrollTop() };
	}

	AP._restore_scroll = function(saved) {
	    if (saved && saved.$el) {
	        saved.$el.scrollTop(saved.top);
	    }
	}

	AP._replace_section = function($root, selector, html) {
	    var $target = $root.find(selector).first();
	    if (!$target.length) return false;
	    var height = $target.outerHeight();
	    if (height > 0) {
	        $target.css("min-height", height + "px");
	        $target.addClass("painel-section--height-lock");
	    }
	    $target.replaceWith(html);
	    var $next = $root.find(selector).first();
	    if ($next.length) {
	        requestAnimationFrame(function () {
	            requestAnimationFrame(function () {
	                $next.css("min-height", "");
	                $next.removeClass("painel-section--height-lock");
	            });
	        });
	    }
	    return true;
	}

	AP._period_section_html = function(list_key, d, page) {
	    var periodo = d.periodo_dias || page.painel_periodo || 7;
	    var limits = d.list_limits || U.painel_merge_list_limits(page);
	    var meta = d.list_meta || {};
	    var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;

	    switch (list_key) {
	        case "hero":
	            return H.render_header(d.resumo, d.kpis, periodo, d.financeiro);
	        case "centro_atencao":
	            return K.render_centro_atencao(
	                d.centro_atencao,
	                d.kpis,
	                d.financeiro,
	                horas,
	                d.total_despesas_mes,
	                periodo
	            );
	        case "prox_audiencia":
	            return A.render_proxima_audiencia(d.audiencias, d.timeline);
	        case "saude_operacional":
	            return K.render_saude_operacional(d.centro_atencao, d.kpis, d.financeiro);
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
	                d.parcelas,
	                d.despesas_pendentes,
	                d.total_despesas_mes,
	                meta.parcelas,
	                meta.despesas,
	                limits.parcelas,
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
	}

	AP._list_section_html = function(list_key, d, page) {
	    var periodo = d.periodo_dias || page.painel_periodo || 7;
	    var limits = d.list_limits || U.painel_merge_list_limits(page);
	    var meta = d.list_meta || {};

	    switch (list_key) {
	        case "timeline":
	        case "comunicacoes":
	            return AP._period_section_html(list_key, d, page);
	        case "parcelas":
	            return F.render_parcelas(d.parcelas, true, meta.parcelas, limits.parcelas);
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
	}

	AP.load = function(page, options) {
	    options = options || {};
	    var soft = !!options.soft;
	    var section = options.section || null;
	    var period = !!options.period;
	    var scroll = soft ? AP._save_scroll(page) : null;

	    if (!soft) {
	        AP.mostrar_skeleton(page.painel_container);
	    } else if (section) {
	        page.painel_container.find("#painel-" + section).addClass("painel-section--updating");
	    }

	    var periodo = page.painel_periodo || 7;
	    var list_limits = U.painel_merge_list_limits(page);
	    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data", {
	        periodo_dias: periodo,
	        list_limits: list_limits,
	    })
	        .then(function (data) {
	            page.painel_data = data;
	            if (section) {
	                AP.patch_list_section(page.painel_container, section, data, page);
	            } else if (period) {
	                AP.patch_period_sections(page.painel_container, data, page);
	            } else {
	                AP.render(page.painel_container, data, page);
	            }
	            if (soft) {
	                AP._restore_scroll(scroll);
	            }
	        })
	        .catch(function (err) {
	            if (soft && (section || period) && page.painel_data) {
	                frappe.show_alert({
	                    message: __("Não foi possível atualizar o painel."),
	                    indicator: "red",
	                });
	            } else {
	                AP.handle_error(page.painel_container, err);
	            }
	        })
	        .finally(function () {
	            page.painel_container.find(".painel-section--updating").removeClass(
	                "painel-section--updating"
	            );
	        });
	}

	AP.render = function($container, d, page, options) {
	    options = options || {};
	    var periodo = d.periodo_dias || page.painel_periodo || 7;
	    var limits = d.list_limits || U.painel_merge_list_limits(page);
	    var meta = d.list_meta || {};
	    var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;
	    page.painel_list_limits = limits;
	    var content_class = options.animate === false ? " painel-content--stable" : "";
	    var html = '<div class="painel-content' + content_class + '">';
	    html += H.render_header(d.resumo, d.kpis, periodo, d.financeiro);
	    html += H.render_filtros_painel(periodo);
	    html += H.render_acoes_rapidas();
	    html += '<div class="painel-zona-critica">';
	    html += K.render_centro_atencao(
	        d.centro_atencao,
	        d.kpis,
	        d.financeiro,
	        horas,
	        d.total_despesas_mes,
	        periodo
	    );
	    html += '<div class="painel-destaques-grid">';
	    html += A.render_proxima_audiencia(d.audiencias, d.timeline);
	    html += K.render_saude_operacional(d.centro_atencao, d.kpis, d.financeiro);
	    html += "</div></div>";
	    html += T.render_timeline(d.timeline, periodo, meta.timeline, limits.timeline);
	    html += T.render_comunicacoes_pendentes(
	        d.comunicacoes_pendentes || d.ultimas_comunicacoes,
	        periodo,
	        meta.comunicacoes,
	        limits.comunicacoes
	    );
	    html += K.render_indicadores_painel(
	        d.centro_atencao,
	        d.kpis,
	        d.financeiro,
	        horas,
	        d.total_despesas_mes,
	        periodo
	    );
	    html += '<div class="painel-zona-secundaria">';
	    html += F.render_financeiro(d.financeiro, periodo);
	    html += F.render_duo_honorarios_despesas(
	        d.parcelas,
	        d.despesas_pendentes,
	        d.total_despesas_mes,
	        meta.parcelas,
	        meta.despesas,
	        limits.parcelas,
	        limits.despesas
	    );
	    html += F.render_duo_custas_horas(
	        d.custas_pendentes_repasse,
	        d.total_custas_mes,
	        horas,
	        meta.custas,
	        periodo,
	        limits.custas
	    );
	    html += "</div>";
	    html += "</div>";
	    $container.html(html);
	    F.painel_init_finance_chart($container, d.financeiro, page);
	}

	AP.patch_period_sections = function($container, d, page) {
	    var periodo = d.periodo_dias || page.painel_periodo || 7;
	    page.painel_list_limits = d.list_limits || U.painel_merge_list_limits(page);
	    page.painel_data = d;

	    $container.find(".painel-periodo-label").text(U.painel_periodo_scope_label(periodo));

	    var sections = [
	        { sel: "#painel-hero", key: "hero" },
	        { sel: "#painel-centro-atencao", key: "centro_atencao" },
	        { sel: "#painel-prox-audiencia", key: "prox_audiencia" },
	        { sel: "#painel-saude-operacional", key: "saude_operacional" },
	        { sel: "#painel-timeline", key: "timeline" },
	        { sel: "#painel-comunicacoes", key: "comunicacoes" },
	        { sel: "#painel-indicadores", key: "indicadores" },
	        { sel: "#painel-financeiro", key: "financeiro" },
	        { sel: "#painel-duo-financeiro", key: "duo_financeiro" },
	        { sel: "#painel-duo-secundario", key: "duo_secundario" },
	    ];

	    var missing = false;
	    sections.forEach(function (s) {
	        var html = AP._period_section_html(s.key, d, page);
	        if (!html || !AP._replace_section($container, s.sel, html)) {
	            missing = true;
	        }
	    });

	    if (missing) {
	        AP.render($container, d, page, { animate: false });
	        return;
	    }

	    F.painel_init_finance_chart($container, d.financeiro, page);
	}

	AP.patch_list_section = function($container, list_key, d, page) {
	    page.painel_list_limits = d.list_limits || U.painel_merge_list_limits(page);
	    page.painel_data = d;

	    var html = AP._list_section_html(list_key, d, page);
	    if (!html) {
	        AP.render($container, d, page, { animate: false });
	        return;
	    }

	    if (!AP._replace_section($container, "#painel-" + list_key, html)) {
	        AP.render($container, d, page, { animate: false });
	    }
	}

	AP.bind_painel_filters = function($root, page) {
	    $root.off("click.painelFilters");
	    $root.on("click.painelFilters", ".painel-periodo-btn", function (e) {
	        e.preventDefault();
	        var dias = U.cint($(this).attr("data-periodo"));
	        if (!page || dias === page.painel_periodo) return;
	        page.painel_periodo = dias;
	        $root.find(".painel-periodo-btn").removeClass("active");
	        $(this).addClass("active");
	        AP.load(page, { soft: true, period: true });
	    });
	    $root.on("click.painelFilters", ".painel-linhas-btn", function (e) {
	        e.preventDefault();
	        var list_key = $(this).attr("data-list");
	        var linhas = U.cint($(this).attr("data-linhas"));
	        if (!page || !list_key) return;
	        if (!page.painel_list_limits) {
	            page.painel_list_limits = U.painel_default_list_limits();
	        }
	        if (linhas === page.painel_list_limits[list_key]) return;
	        page.painel_list_limits[list_key] = linhas;
	        var $group = $(this).closest(".painel-linhas-filters");
	        $group.find(".painel-linhas-btn").removeClass("active");
	        $(this).addClass("active");
	        AP.load(page, { soft: true, section: list_key });
	    });
	}

	AP.bind_atencao_routes = function($root, page) {
	    $root.off("click.painelAtencao");
	    $root.on("click.painelAtencao", ".painel-atencao-card[data-atencao-route]", function () {
	        var hoje = frappe.datetime.get_today();
	        var amanha = frappe.datetime.add_days(hoje, 1);
	        var tres_dias = frappe.datetime.add_days(hoje, 3);
	        var periodo_fim = U.painel_periodo_fim(page);
	        var mes_inicio = frappe.datetime.month_start(hoje);
	        var mes_fim = frappe.datetime.month_end(hoje);
	        var key = $(this).attr("data-atencao-route");

	        var routes = {
	            audiencias_hoje: function () {
	                U.painel_goto_list("Audiencia", [
	                    ["data_hora", "between", [hoje + " 00:00:00", hoje + " 23:59:59"]],
	                ]);
	            },
	            audiencias_amanha: function () {
	                U.painel_goto_list("Audiencia", [
	                    ["data_hora", "between", [amanha + " 00:00:00", amanha + " 23:59:59"]],
	                ]);
	            },
	            audiencias_periodo: function () {
	                U.painel_goto_list("Audiencia", [
	                    ["data_hora", "between", [hoje + " 00:00:00", periodo_fim + " 23:59:59"]],
	                ]);
	            },
	            prazos_vencidos: function () {
	                U.painel_goto_list("Controle de Prazos", [
	                    ["status", "=", "Pendente"],
	                    ["data_prazo", "<", hoje],
	                ]);
	            },
	            prazos_proximos: function () {
	                U.painel_goto_list("Controle de Prazos", [
	                    ["status", "=", "Pendente"],
	                    ["data_prazo", "between", [hoje, tres_dias]],
	                ]);
	            },
	            prazos_criticos: function () {
	                U.painel_goto_list("Controle de Prazos", [
	                    ["status", "=", "Pendente"],
	                    ["data_prazo", "<=", tres_dias],
	                ]);
	            },
	            tarefas_atrasadas: function () {
	                U.painel_goto_list("Tarefa", [
	                    ["status", "in", ["Pendente", "Em Andamento"]],
	                    ["data_limite", "<", hoje],
	                ]);
	            },
	            tarefas_pendentes: function () {
	                U.painel_goto_list("Tarefa", [["status", "in", ["Pendente", "Em Andamento"]]]);
	            },
	            parcelas_vencidas: function () {
	                U.painel_goto_list("Pagamento", [["status", "=", "Vencido"]]);
	            },
	            pagamentos_periodo: function () {
	                U.painel_goto_list("Pagamento", [
	                    ["status", "=", "Pendente"],
	                    ["data_vencimento", "between", [hoje, periodo_fim]],
	                ]);
	            },
	            recebimentos_periodo: function () {
	                U.painel_goto_list("Pagamento", [
	                    ["status", "in", ["Recebido", "Repassado"]],
	                    ["data_recebimento", "between", [hoje, periodo_fim]],
	                ]);
	            },
	            receita_mes: function () {
	                U.painel_goto_list("Pagamento", [
	                    ["status", "in", ["Recebido", "Repassado"]],
	                    ["data_recebimento", "between", [mes_inicio, mes_fim]],
	                ]);
	            },
	            honorarios_ativos: function () {
	                U.painel_goto_list("Acordo de Honorarios Processuais", [["status", "=", "Vigente"]]);
	            },
	            horas: function () {
	                U.painel_goto_list("Registro de Horas", [
	                    ["data", "between", [hoje, periodo_fim]],
	                ]);
	            },
	            clientes: function () {
	                U.painel_goto_list("Cliente", []);
	            },
	            taxa_recebimento: function () {
	                frappe.set_route("query-report", "inadimplencia");
	            },
	            processos_ativos: function () {
	                U.painel_goto_list("Servico", [["status", "=", "Em andamento"]]);
	            },
	            custas_abertas: function () {
	                U.painel_goto_list("Custa Processual", [
	                    ["status", "in", ["Pendente", "Pago"]],
	                    ["repassar_cliente", "=", 1],
	                ]);
	            },
	            despesas_mes: function () {
	                U.painel_goto_list("Despesa do Escritorio", [
	                    ["data_vencimento", "between", [mes_inicio, mes_fim]],
	                ]);
	            },
	        };

	        if (routes[key]) routes[key]();
	    });
	}

})(advocacia.painel);

$(document).on("click", ".painel-timeline-item[data-dt], .painel-tl-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-prox-card[data-dt], .painel-prox-body[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", "[data-route-calendar]", function (e) {
    e.stopPropagation();
    frappe.set_route("List", "Audiencia", "Calendar");
});

$(document).on("click", ".painel-schedule-item[data-dt], .painel-com-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-action-chip", function () {
    var dt = $(this).attr("data-new-dt");
    if (dt) frappe.new_doc(dt);
});

$(document).on("click", ".painel-section-link[data-scroll]", function () {
    advocacia.painel.utils.scroll_painel_section($(this).attr("data-scroll"));
});

$(document).on("click", "[data-route-list]", function (e) {
    e.stopPropagation();
    var dt = $(this).attr("data-route-list");
    if (dt) advocacia.painel.utils.painel_goto_list(dt, []);
});

$(document).on("click", ".painel-schedule-card[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-op-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-parcela-critica", function (e) {
    if ($(e.target).closest(".painel-btn-recebida").length) return;
    var acordo = $(this).attr("data-acordo");
    if (acordo) frappe.set_route("Form", "Acordo de Honorarios Processuais", acordo);
});

$(document).on("click", ".painel-row-acordo", function (e) {
    if ($(e.target).closest(".painel-btn-recebida").length) return;
    var acordo = $(this).attr("data-acordo");
    if (acordo) frappe.set_route("Form", "Acordo de Honorarios Processuais", acordo);
});

$(document).on("click", ".painel-btn-recebida", function (e) {
    e.stopPropagation();
    var btn = $(this);
    var pagamento = btn.attr("data-pagamento") || btn.attr("data-parcela");
    if (!pagamento) return;

    frappe.confirm(
        __("Marcar pagamento como recebido hoje?"),
        function () {
            btn.prop("disabled", true).text("...");
            frappe
                .xcall("advocacia.advocacia.painel_api.marcar_parcela_recebida", {
                    parcela_name: pagamento,
                })
                .then(function () {
                    frappe.show_alert({
                        message: __("Pagamento marcado como Recebido"),
                        indicator: "green",
                    });
                    var page =
                        (frappe.pages.painel && frappe.pages.painel.page) ||
                        (cur_page && cur_page.page ? cur_page.page : null);
                    if (page && advocacia.painel.load) {
                        advocacia.painel.load(page);
                    }
                })
                .catch(function (err) {
                    btn.prop("disabled", false).text("✓ " + __("Recebido"));
                    frappe.msgprint(err.message || __("Erro ao marcar parcela"));
                });
        }
    );
});
