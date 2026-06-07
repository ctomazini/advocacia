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

	AP.load = function(page) {
	    AP.mostrar_skeleton(page.painel_container);
	    var periodo = page.painel_periodo || 7;
	    var list_limits = U.painel_merge_list_limits(page);
	    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data", {
	        periodo_dias: periodo,
	        list_limits: list_limits,
	    })
	        .then(function (data) {
	            page.painel_data = data;
	            AP.render(page.painel_container, data, page);
	        })
	        .catch(function (err) {
	            AP.handle_error(page.painel_container, err);
	        });
	}

	AP.render = function($container, d, page) {
	    var periodo = d.periodo_dias || page.painel_periodo || 7;
	    var limits = d.list_limits || U.painel_merge_list_limits(page);
	    var meta = d.list_meta || {};
	    var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;
	    page.painel_list_limits = limits;
	    var html = '<div class="painel-content">';
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
	    AP.bind_painel_filters($container, page);
	    AP.bind_atencao_routes($container, page);
	    F.painel_init_finance_chart($container, d.financeiro, page);
	}

	AP.bind_painel_filters = function($root, page) {
	    $root.find(".painel-periodo-btn").on("click", function () {
	        var dias = U.cint($(this).attr("data-periodo"));
	        if (!page || dias === page.painel_periodo) return;
	        page.painel_periodo = dias;
	        AP.load(page);
	    });
	    $root.find(".painel-linhas-btn").on("click", function () {
	        var list_key = $(this).attr("data-list");
	        var linhas = U.cint($(this).attr("data-linhas"));
	        if (!page || !list_key) return;
	        if (!page.painel_list_limits) {
	            page.painel_list_limits = U.painel_default_list_limits();
	        }
	        if (linhas === page.painel_list_limits[list_key]) return;
	        page.painel_list_limits[list_key] = linhas;
	        AP.load(page);
	    });
	}

	AP.bind_atencao_routes = function($root, page) {
	    var hoje = frappe.datetime.get_today();
	    var amanha = frappe.datetime.add_days(hoje, 1);
	    var tres_dias = frappe.datetime.add_days(hoje, 3);
	    var periodo_fim = U.painel_periodo_fim(page);
	    var mes_inicio = frappe.datetime.month_start(hoje);
	    var mes_fim = frappe.datetime.month_end(hoje);

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

	    $root.find(".painel-atencao-card[data-atencao-route]").on("click", function () {
	        var key = $(this).attr("data-atencao-route");
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
