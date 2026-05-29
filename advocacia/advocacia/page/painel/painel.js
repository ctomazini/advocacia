frappe.pages.painel = frappe.pages.painel || {};

frappe.pages.painel.on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Painel do Escritório"),
        single_column: true,
    });

    page.painel_container = $('<div class="painel-container"></div>').appendTo(page.main);
    inject_painel_styles();

    page.add_button(__("+ Serviço"), function () {
        frappe.new_doc("Servico");
    });
    page.add_button(__("+ Honorários"), function () {
        frappe.new_doc("Acordo de Honorarios Processuais");
    });
    page.add_button(__("+ Audiência"), function () {
        frappe.new_doc("Audiencia");
    });
    page.add_button(__("+ Prazo"), function () {
        frappe.new_doc("Controle de Prazos");
    });
    page.add_button(__("↺ Atualizar"), function () {
        load_painel(page);
    });

    frappe.pages.painel.page = page;
    load_painel(page);
};

function inject_painel_styles() {
    if (document.getElementById("painel-advocacia-styles")) return;
    var css = `
        .painel-container {
            padding: 16px;
            max-width: 1280px;
            background: var(--bg-default);
        }
        .painel-section {
            margin-bottom: 32px;
        }
        .painel-section-title {
            font-size: var(--text-base);
            font-weight: 600;
            color: var(--text-color);
            margin: 0 0 12px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .painel-kpi-card {
            border-radius: var(--border-radius-lg);
            border: 1px solid var(--border-color);
            background: var(--card-bg);
            padding: 16px;
            min-height: 88px;
            cursor: pointer;
            transition: box-shadow 0.2s ease;
            box-shadow: var(--shadow-sm);
        }
        .painel-kpi-card:hover {
            box-shadow: var(--shadow-sm);
        }
        .painel-kpi-value {
            font-size: var(--text-lg);
            font-weight: 700;
            color: var(--text-color);
            line-height: 1.2;
        }
        .painel-kpi-label {
            font-size: var(--text-sm);
            color: var(--text-muted);
            margin-top: 8px;
        }
        .painel-kpi-icon {
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        .painel-kpi-card.painel-kpi-green .painel-kpi-value {
            color: var(--green-500);
        }
        .painel-kpi-card.painel-kpi-green .painel-kpi-icon {
            color: var(--green-500);
        }
        .painel-parcelas-actions {
            white-space: nowrap;
        }
        .painel-alertas {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .painel-alerta {
            border-radius: var(--border-radius-lg);
            border: 1px solid var(--border-color);
            padding: 12px 16px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            cursor: pointer;
            min-height: 44px;
        }
        .painel-alerta.red {
            background: color-mix(in srgb, var(--red-500) 12%, var(--card-bg));
            border-color: var(--red-500);
        }
        .painel-alerta.yellow {
            background: color-mix(in srgb, var(--yellow-500) 12%, var(--card-bg));
            border-color: var(--yellow-500);
        }
        .painel-card {
            border-radius: var(--border-radius-lg);
            border: 1px solid var(--border-color);
            background: var(--card-bg);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }
        .painel-table {
            width: 100%;
            border-collapse: collapse;
            font-size: var(--text-sm);
        }
        .painel-table th {
            text-align: left;
            padding: 12px 16px;
            background: var(--subtle-fg);
            color: var(--text-muted);
            font-weight: 600;
            font-size: var(--text-sm);
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }
        .painel-table td {
            padding: 12px 16px;
            border-top: 1px solid var(--border-color);
            color: var(--text-color);
            vertical-align: middle;
        }
        .painel-table tr.painel-row-click {
            cursor: pointer;
        }
        .painel-table tr.painel-row-click:hover td {
            background: var(--subtle-fg);
        }
        .painel-section-table {
            overflow-x: auto;
        }
        .painel-list-item {
            padding: 12px 16px;
            border-top: 1px solid var(--border-color);
            cursor: pointer;
            min-height: 44px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px 16px;
        }
        .painel-list-item:first-child {
            border-top: none;
        }
        .painel-list-item:hover {
            background: var(--subtle-fg);
        }
        .painel-muted {
            color: var(--text-muted);
            font-size: var(--text-sm);
        }
        .painel-btn-entrar {
            min-height: 44px;
            min-width: 44px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 12px;
            border-radius: var(--border-radius);
            background: var(--btn-primary-bg);
            color: var(--btn-primary-color);
            text-decoration: none;
            font-size: var(--text-sm);
            font-weight: 600;
        }
        .painel-empty {
            text-align: center;
            padding: 32px 16px;
            color: var(--text-muted);
            font-size: var(--text-sm);
        }
        .painel-skeleton-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        .painel-skeleton-block {
            height: 88px;
            border-radius: var(--border-radius-lg);
            background: var(--gray-100);
            animation: painel-pulse 1.5s ease-in-out infinite;
        }
        .painel-skeleton-section {
            height: 200px;
            border-radius: var(--border-radius-lg);
            background: var(--gray-100);
            animation: painel-pulse 1.5s ease-in-out infinite;
            margin-bottom: 24px;
        }
        @keyframes painel-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.45; }
        }
        @media (max-width: 768px) {
            .kpi-grid { grid-template-columns: 1fr 1fr; }
            .painel-section-table { overflow-x: auto; }
        }
        @media (max-width: 480px) {
            .kpi-grid { grid-template-columns: 1fr; }
        }
    `;
    $('<style id="painel-advocacia-styles">' + css + "</style>").appendTo("head");
}

function load_painel(page) {
    mostrar_skeleton(page.painel_container);
    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data")
        .then(function (data) {
            render_painel(page.painel_container, data);
        })
        .catch(function (err) {
            handle_error(page.painel_container, err);
        });
}

function mostrar_skeleton($container) {
    var html = '<div class="painel-skeleton-grid">';
    for (var i = 0; i < 7; i++) html += '<div class="painel-skeleton-block"></div>';
    html += "</div>";
    html += '<div class="painel-skeleton-section"></div>';
    html += '<div class="painel-skeleton-section"></div>';
    $container.html(html);
}

function handle_error($container, err) {
    var msg = (err && err.message) || String(err);
    $container.html(
        '<div class="painel-card"><div class="painel-empty" style="color: var(--red-500);">' +
            __("Erro ao carregar o painel: {0}", [msg]) +
            "</div></div>"
    );
}

function render_painel($container, d) {
    var html = "";
    var kpi_routes = get_kpi_routes();
    html += render_kpis(d.kpis);
    html += render_alertas(d.alertas);
    html += render_parcelas(d.parcelas);
    html += render_audiencias(d.audiencias);
    html += render_prazos(d.prazos);
    html += render_tarefas(d.tarefas);
    $container.html(html);
    bind_kpi_routes($container, kpi_routes);
}

function painel_icon(name) {
    try {
        return frappe.utils.icon(name, "sm") || "";
    } catch (e) {
        return "";
    }
}

function fmt_currency(val) {
    return frappe.format(val || 0, { fieldtype: "Currency", currency: "BRL" });
}

function fmt_date_iso(iso) {
    if (!iso) return "";
    return frappe.datetime.str_to_user(iso);
}

function fmt_datetime(iso, hora) {
    if (!iso) return "";
    var s = fmt_date_iso(iso);
    if (hora) s += " " + hora;
    return s;
}

function status_pill(status) {
    var map = {
        Vencida: "red",
        Pendente: "orange",
        Recebida: "green",
        Repassada: "blue",
        Cancelada: "gray",
        "Em Andamento": "blue",
        Pendente: "orange",
        Concluída: "green",
        Cancelada: "gray",
        Alta: "red",
        "Média": "orange",
        Media: "orange",
        Urgente: "red",
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

function get_kpi_routes() {
    return [
        function () {
            frappe.set_route("List", "Cliente");
        },
        function () {
            frappe.route_options = { status: "Em andamento" };
            frappe.set_route("List", "Servico");
        },
        function () {
            scroll_painel_section("painel-parcelas");
        },
        function () {
            scroll_painel_section("painel-parcelas");
        },
        function () {
            scroll_painel_section("painel-parcelas");
        },
        function () {
            scroll_painel_section("painel-audiencias");
        },
        function () {
            frappe.route_options = { status: "Pendente" };
            frappe.set_route("List", "Controle de Prazos");
        },
    ];
}

function render_kpis(k) {
    if (!k) return "";
    var items = [
        { key: "clientes", icon: "users", label: __("Clientes"), value: k.total_clientes },
        { key: "servicos", icon: "folder", label: __("Serviços ativos"), value: k.servicos_ativos },
        {
            key: "vencidas",
            icon: "warning",
            label: __("Parcelas vencidas"),
            value: fmt_currency(k.parcelas_vencidas.valor),
            sub: __("{0} parcela(s)", [k.parcelas_vencidas.count]),
        },
        {
            key: "avencer",
            icon: "calendar",
            label: __("A vencer (30 dias)"),
            value: fmt_currency(k.parcelas_a_vencer_30d.valor),
            sub: __("{0} parcela(s)", [k.parcelas_a_vencer_30d.count]),
        },
        {
            key: "recebido",
            icon: "money",
            label: __("Recebido este mês"),
            value: fmt_currency(k.recebido_mes.valor),
            sub: __("{0} parcela(s)", [k.recebido_mes.count]),
            green: true,
        },
        { key: "audiencias", icon: "milestone", label: __("Audiências (7 dias)"), value: k.audiencias_semana },
        { key: "prazos", icon: "time", label: __("Prazos urgentes"), value: k.prazos_urgentes },
    ];

    var h = '<div class="painel-section"><div class="kpi-grid">';
    items.forEach(function (item) {
        h +=
            '<div class="painel-kpi-card' +
            (item.green ? " painel-kpi-green" : "") +
            '" data-kpi="' +
            item.key +
            '">' +
            '<div class="painel-kpi-icon">' +
            painel_icon(item.icon) +
            "</div>" +
            '<div class="painel-kpi-value">' +
            item.value +
            "</div>" +
            '<div class="painel-kpi-label">' +
            item.label +
            (item.sub ? '<br><span class="painel-muted">' + item.sub + "</span>" : "") +
            "</div></div>";
    });
    h += "</div></div>";
    return h;
}

function bind_kpi_routes($root, routes) {
    $root.find(".painel-kpi-card").each(function (idx) {
        $(this)
            .off("click")
            .on("click", function () {
                if (routes[idx]) routes[idx]();
            });
    });
}

function render_alertas(alertas) {
    if (!alertas || !alertas.length) return "";
    var h =
        '<div class="painel-section"><h3 class="painel-section-title">' +
        painel_icon("alert-triangle") +
        " " +
        __("Alertas") +
        '</h3><div class="painel-alertas">';
    alertas.forEach(function (a) {
        var nivel = a.nivel === "red" ? "red" : "yellow";
        var texto = "";
        if (a.tipo === "prazo") {
            var quando =
                a.dias === 0
                    ? __("Vence hoje")
                    : a.dias === 1
                      ? __("Vence amanhã")
                      : __("Vence em {0} dias", [a.dias]);
            texto =
                "<strong>" +
                frappe.utils.escape_html(a.titulo) +
                "</strong> — " +
                quando +
                (a.cliente ? " · " + frappe.utils.escape_html(a.cliente) : "");
        } else {
            texto =
                "<strong>" +
                __("Audiência hoje") +
                "</strong> — " +
                frappe.utils.escape_html(a.titulo) +
                (a.hora ? " " + a.hora : "") +
                (a.cliente ? " · " + frappe.utils.escape_html(a.cliente) : "") +
                (a.vara ? " · " + frappe.utils.escape_html(a.vara) : "");
        }
        h +=
            '<div class="painel-alerta ' +
            nivel +
            '" data-dt="' +
            a.doctype +
            '" data-dn="' +
            frappe.utils.escape_html(a.docname) +
            '">' +
            painel_icon(a.tipo === "prazo" ? "time" : "milestone") +
            '<div style="flex:1;font-size:var(--text-sm);color:var(--text-color);">' +
            texto +
            "</div></div>";
    });
    h += "</div></div>";
    return h;
}

function render_parcelas(parcelas) {
    var h =
        '<div class="painel-section" id="painel-parcelas"><h3 class="painel-section-title">' +
        painel_icon("money") +
        " " +
        __("Parcelas") +
        "</h3>";
    if (!parcelas || !parcelas.length) {
        return h + '<div class="painel-card"><div class="painel-empty">' + __("Nenhuma parcela pendente.") + "</div></div></div>";
    }
    h += '<div class="painel-card painel-section-table"><table class="painel-table"><thead><tr>';
    h +=
        "<th>" +
        __("Cliente") +
        "</th><th>" +
        __("Serviço") +
        "</th><th>" +
        __("Vencimento") +
        "</th><th>" +
        __("Valor") +
        "</th><th>" +
        __("Status") +
        "</th><th>" +
        __("Prazo") +
        "</th><th>" +
        __("Ações") +
        "</th></tr></thead><tbody>";
    parcelas.forEach(function (p) {
        var servico =
            frappe.utils.escape_html(p.servico_titulo || p.servico_tipo || p.servico_ref || "—");
        if (p.numero_processo) {
            servico += '<br><span class="painel-muted">' + frappe.utils.escape_html(p.numero_processo) + "</span>";
        }
        var prazo_txt = "";
        if (p.status === "Vencida" && p.dias_atraso > 0) {
            prazo_txt = __("Atraso {0}d", [p.dias_atraso]);
        } else if (p.status === "Pendente") {
            prazo_txt =
                p.dias_para_vencer === 0
                    ? __("Hoje")
                    : __("Em {0}d", [p.dias_para_vencer]);
        }
        var btn_recebida = "";
        if (p.status === "Vencida" || p.status === "Pendente") {
            btn_recebida =
                '<button type="button" class="btn btn-xs btn-success painel-btn-recebida" data-parcela="' +
                frappe.utils.escape_html(p.name || "") +
                '">✓ ' +
                __("Recebida") +
                "</button>";
        }
        h +=
            '<tr class="painel-row-click" data-acordo="' +
            frappe.utils.escape_html(p.parent || "") +
            '">' +
            "<td>" +
            frappe.utils.escape_html(p.cliente_nome || "—") +
            "</td>" +
            "<td>" +
            servico +
            "</td>" +
            "<td>" +
            fmt_date_iso(p.vencimento) +
            "</td>" +
            "<td>" +
            fmt_currency(p.valor_total) +
            "</td>" +
            "<td>" +
            status_pill(p.status) +
            "</td>" +
            '<td class="painel-muted">' +
            frappe.utils.escape_html(prazo_txt) +
            '</td><td class="painel-parcelas-actions">' +
            btn_recebida +
            "</td></tr>";
    });
    h += "</tbody></table></div></div>";
    return h;
}

function render_audiencias(audiencias) {
    var h =
        '<div class="painel-section" id="painel-audiencias"><h3 class="painel-section-title">' +
        painel_icon("milestone") +
        " " +
        __("Audiências — próximos 7 dias") +
        "</h3>";
    if (!audiencias || !audiencias.length) {
        return h + '<div class="painel-card"><div class="painel-empty">' + __("Nenhuma audiência nesta semana.") + "</div></div></div>";
    }
    h += '<div class="painel-card">';
    audiencias.forEach(function (a) {
        var mod = a.modalidade || "";
        var mod_cls = mod === "Virtual" ? "blue" : mod === "Híbrida" ? "orange" : "gray";
        var btn =
            mod === "Virtual" && a.link_virtual
                ? '<a class="painel-btn-entrar" href="' +
                  frappe.utils.escape_html(a.link_virtual) +
                  '" target="_blank" rel="noopener" onclick="event.stopPropagation();">' +
                  __("Entrar") +
                  "</a>"
                : "";
        h +=
            '<div class="painel-list-item" data-dt="Audiencia" data-dn="' +
            frappe.utils.escape_html(a.name) +
            '">' +
            '<div style="min-width:120px;"><strong>' +
            fmt_datetime(a.data, a.hora) +
            "</strong></div>" +
            "<div style='flex:1;min-width:140px;'>" +
            frappe.utils.escape_html(a.cliente || "—") +
            '<br><span class="painel-muted">' +
            frappe.utils.escape_html(a.tipo || "") +
            "</span></div>" +
            '<div class="painel-muted">' +
            frappe.utils.escape_html(a.vara_label || "—") +
            "</div>" +
            '<span class="indicator-pill ' +
            mod_cls +
            ' filterable no-indicator-dot ellipsis">' +
            frappe.utils.escape_html(mod || __("Presencial")) +
            "</span>" +
            btn +
            "</div>";
    });
    h += "</div></div>";
    return h;
}

function render_prazos(prazos) {
    var h =
        '<div class="painel-section" id="painel-prazos"><h3 class="painel-section-title">' +
        painel_icon("time") +
        " " +
        __("Prazos") +
        "</h3>";
    if (!prazos || !prazos.length) {
        return h + '<div class="painel-card"><div class="painel-empty">' + __("Nenhum prazo pendente.") + "</div></div></div>";
    }
    h += '<div class="painel-card">';
    prazos.forEach(function (p) {
        var dias = p.dias_restantes;
        var dias_txt =
            dias < 0
                ? __("Vencido há {0}d", [Math.abs(dias)])
                : dias === 0
                  ? __("Hoje")
                  : dias === 1
                    ? __("Amanhã")
                    : __("Em {0}d", [dias]);
        h +=
            '<div class="painel-list-item" data-dt="Controle de Prazos" data-dn="' +
            frappe.utils.escape_html(p.name) +
            '">' +
            '<div style="flex:1;min-width:180px;"><strong>' +
            frappe.utils.escape_html(p.descricao || p.name) +
            "</strong><br><span class='painel-muted'>" +
            frappe.utils.escape_html(p.cliente_nome || "—") +
            "</span></div>" +
            '<div class="painel-muted">' +
            dias_txt +
            " · " +
            fmt_date_iso(p.data_prazo) +
            "</div>" +
            status_pill(p.prioridade) +
            "</div>";
    });
    h += "</div></div>";
    return h;
}

function render_tarefas(tarefas) {
    var h =
        '<div class="painel-section" id="painel-tarefas"><h3 class="painel-section-title">' +
        painel_icon("checklist") +
        " " +
        __("Tarefas") +
        "</h3>";
    if (!tarefas || !tarefas.length) {
        return h + '<div class="painel-card"><div class="painel-empty">' + __("Nenhuma tarefa aberta.") + "</div></div></div>";
    }
    h += '<div class="painel-card">';
    tarefas.forEach(function (t) {
        var prazo = "";
        if (t.data_limite) {
            var d = t.dias_restantes;
            if (d !== null && d !== undefined) {
                if (d < 0) prazo = __("Atrasada {0}d", [Math.abs(d)]);
                else if (d === 0) prazo = __("Hoje");
                else if (d === 1) prazo = __("Amanhã");
                else prazo = __("Em {0}d", [d]);
            }
            prazo += " · " + fmt_date_iso(t.data_limite);
        } else {
            prazo = __("Sem prazo");
        }
        h +=
            '<div class="painel-list-item" data-dt="Tarefa" data-dn="' +
            frappe.utils.escape_html(t.name) +
            '">' +
            '<div style="flex:1;min-width:160px;"><strong>' +
            frappe.utils.escape_html(t.titulo || "") +
            "</strong></div>" +
            status_pill(t.status) +
            '<div class="painel-muted">' +
            frappe.utils.escape_html(prazo) +
            "</div>" +
            '<div class="painel-muted">' +
            frappe.utils.escape_html(t.responsavel_nome || "—") +
            "</div></div>";
    });
    h += "</div></div>";
    return h;
}

function scroll_painel_section(id) {
    var el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

$(document).on("click", ".painel-alerta", function () {
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-list-item", function () {
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", "tr.painel-row-click", function (e) {
    if ($(e.target).closest(".painel-btn-recebida").length) return;
    var acordo = $(this).attr("data-acordo");
    if (acordo) frappe.set_route("Form", "Acordo de Honorarios Processuais", acordo);
});

$(document).on("click", ".painel-btn-recebida", function (e) {
    e.stopPropagation();
    var btn = $(this);
    var parcela = btn.attr("data-parcela");
    if (!parcela) return;

    frappe.confirm(
        __("Marcar parcela como recebida hoje?"),
        function () {
            btn.prop("disabled", true).text("...");
            frappe
                .xcall("advocacia.advocacia.painel_api.marcar_parcela_recebida", {
                    parcela_name: parcela,
                })
                .then(function () {
                    frappe.show_alert({
                        message: __("Parcela marcada como Recebida"),
                        indicator: "green",
                    });
                    var page =
                        (frappe.pages.painel && frappe.pages.painel.page) ||
                        (cur_page && cur_page.page ? cur_page.page : null);
                    if (page && typeof load_painel === "function") load_painel(page);
                })
                .catch(function (err) {
                    btn.prop("disabled", false).text("✓ " + __("Recebida"));
                    frappe.msgprint(err.message || __("Erro ao marcar parcela"));
                });
        }
    );
});
