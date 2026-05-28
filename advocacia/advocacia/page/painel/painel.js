frappe.pages['painel'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Painel Advocacia',
        single_column: true
    });

    page.add_button("+ Serviço",    function(){ frappe.new_doc("Servico"); },                          {btn_class:"btn-default"});
    page.add_button("+ Cliente",    function(){ frappe.new_doc("Cliente"); },                          {btn_class:"btn-default"});
    page.add_button("+ Honorários", function(){ frappe.new_doc("Acordo de Honorarios Processuais"); }, {btn_class:"btn-default"});
    page.add_button("+ Audiência",  function(){ frappe.new_doc("Audiencia"); },                        {btn_class:"btn-default"});
    page.add_button("+ Prazo",      function(){ frappe.new_doc("Controle de Prazos"); },               {btn_class:"btn-default"});
    page.add_button("+ Tarefa",     function(){ frappe.new_doc("Tarefa"); },                           {btn_class:"btn-default"});
    page.add_button("↺ Atualizar",  function(){ render_painel(page); },                                {btn_class:"btn-default"});

    $(wrapper).find('.page-content').html('<div id="painel-root" style="padding:20px;max-width:1200px"></div>');
    render_painel(page);
};

function fc(v) {
    return 'R$ ' + parseFloat(v||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function fmt_data(d) {
    if (!d) return '';
    var parts = String(d).split('-');
    return parts.length === 3 ? parts[2]+'/'+parts[1]+'/'+parts[0] : d;
}

function fmt_hora(h) {
    if (!h) return '';
    return String(h).substring(0, 5);
}

function scroll_to(id) {
    var el = document.getElementById(id);
    if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
}

function render_painel(page) {
    var root = document.getElementById('painel-root');
    root.innerHTML = '<p style="color:#888">Carregando...</p>';

    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data").then(function(d) {
        var t = d.totais;
        var h = '';

        // KPIs
        h += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px">';
        h += kpi(fc(t.vencido),   'Vencido',            '#dc2626', 'sec-vencidas',  d.vencidas.length);
        h += kpi(fc(t.proximos),  'Vence em 7 dias',    '#d97706', 'sec-proximas',  d.proximas.length);
        h += kpi(fc(t.futuro),    'A receber (futuro)', '#2563eb', 'sec-futuro',    null);
        h += kpi(fc(t.repasse),   'Repasse pendente',   '#7c3aed', 'sec-repasses',  d.repasses.length);
        h += kpi(d.clientes,      'Clientes',           '#6b7280', null,            null, 'Cliente');
        h += kpi(d.servicos,      'Serviços',           '#6b7280', null,            null, 'Servico');
        h += '</div>';

        // Vencidas
        h += '<div id="sec-vencidas">';
        if (d.vencidas.length) {
            h += secao('⚠️ Honorários Vencidos (' + d.vencidas.length + ')', '#dc2626');
            h += tabela_parcelas(d.vencidas, '#dc2626', true);
        }
        h += '</div>';

        // Próximos 7 dias
        h += '<div id="sec-proximas">';
        if (d.proximas.length) {
            h += secao('📅 Vence nos Próximos 7 Dias (' + d.proximas.length + ')', '#d97706');
            h += tabela_parcelas(d.proximas, '#d97706', false);
        }
        h += '</div>';

        h += '<div id="sec-futuro"></div>';

        // Repasses
        h += '<div id="sec-repasses">';
        if (d.repasses.length) {
            h += secao('↗ Repasses Pendentes (' + d.repasses.length + ')', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            h += grid_header(['Cliente','Serviço','Parcela','Valor Cliente'], '1.2fr 1fr 1fr auto');
            d.repasses.forEach(function(p) {
                h += '<div style="display:grid;grid-template-columns:1.2fr 1fr 1fr auto;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\'' + p.parent + '\')">';
                h += '<span style="font-weight:500">' + (p.cliente_nome || '-') + '</span>';
                h += '<span style="color:#6b7280;font-size:12px">' + (p.servico_titulo || p.servico_ref || '') + '</span>';
                h += '<span style="font-size:12px;color:#374151">' + (p['descrição'] || p.descricao || '') + '</span>';
                h += '<span style="color:#7c3aed;font-weight:700;text-align:right">' + fc(p.valor_cliente) + '</span>';
                h += '</div>';
            });
            h += '</div>';
        }
        h += '</div>';

        // Audiências
        if (d.audiencias && d.audiencias.length) {
            h += secao('🏛️ Audiências Esta Semana (' + d.audiencias.length + ')', '#0891b2');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            h += grid_header(['Data/Hora','Cliente','Processo','Modalidade','Tipo/Local',''], '140px 1fr 1fr 100px 1fr 80px');
            d.audiencias.forEach(function(a) {
                var dias = a.dias_restantes || 0;
                var badge_dias = dias === 0 ? '<span style="background:#dc262622;color:#dc2626;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;margin-left:4px">HOJE</span>'
                    : dias === 1 ? '<span style="background:#d9770622;color:#d97706;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;margin-left:4px">AMANHÃ</span>'
                    : '<span style="color:#6b7280;font-size:11px;margin-left:4px">em ' + dias + 'd</span>';

                var is_virtual = a.modalidade === 'Virtual';
                var badge_mod = is_virtual
                    ? '<span style="background:#7c3aed22;color:#7c3aed;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">🖥️ Virtual</span>'
                    : '<span style="background:#0891b222;color:#0891b2;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">🏢 Presencial</span>';

                var btn_entrar = '';
                if (is_virtual && a.link_virtual) {
                    btn_entrar = '<a href="' + a.link_virtual + '" target="_blank" onclick="event.stopPropagation()" style="background:#7c3aed;color:#fff;padding:5px 12px;border-radius:6px;font-size:11px;font-weight:600;text-decoration:none;white-space:nowrap;display:inline-block">Entrar ↗</a>';
                }

                var local_info = (a.tipo || '');
                if (a.local_vara) local_info += ' — ' + a.local_vara;

                h += '<div style="display:grid;grid-template-columns:140px 1fr 1fr 100px 1fr 80px;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Audiencia\',\'' + a.name + '\')">';
                h += '<div><span style="font-weight:600;color:#0891b2">' + fmt_data((a.data_hora || '').substring(0,10)) + '</span><br><span style="font-size:12px;color:#6b7280">' + fmt_hora((a.data_hora || '').substring(11,16)) + badge_dias + '</span></div>';
                h += '<span style="font-weight:500">' + (a.cliente_nome || a.cliente || '-') + '</span>';
                h += '<span style="font-size:12px;color:#6b7280">' + (a.numero_processo || a.servico || '') + '</span>';
                h += '<span>' + badge_mod + '</span>';
                h += '<span style="font-size:12px;color:#374151">' + local_info + '</span>';
                h += '<span style="text-align:center">' + btn_entrar + '</span>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Prazos
        if (d.prazos.length) {
            h += secao('⏰ Prazos Esta Semana (' + d.prazos.length + ')', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            h += grid_header(['Prazo','Cliente','Serviço','Vence em','Prioridade'], '1.5fr 1fr 1fr 80px 90px');
            d.prazos.forEach(function(p) {
                var cor = p.prioridade === 'Alta' ? '#dc2626' : p.prioridade === 'Média' ? '#d97706' : '#6b7280';
                var dias = p.dias_restantes || 0;
                var badge_dias = dias === 0 ? '<span style="color:#dc2626;font-weight:700">HOJE</span>'
                    : dias === 1 ? '<span style="color:#d97706;font-weight:600">Amanhã</span>'
                    : dias < 0 ? '<span style="color:#dc2626;font-weight:700">VENCIDO ' + Math.abs(dias) + 'd</span>'
                    : '<span style="color:#6b7280">' + dias + ' dias</span>';

                h += '<div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 80px 90px;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Controle de Prazos\',\'' + p.name + '\')">';
                h += '<div><span style="font-weight:500">' + (p.descricao || '') + '</span><br><span style="font-size:11px;color:#9ca3af">' + fmt_data(p.data_prazo) + '</span></div>';
                h += '<span style="font-size:12px">' + (p.cliente_nome || '-') + '</span>';
                h += '<span style="font-size:12px;color:#6b7280">' + (p.servico_tipo || '') + (p.numero_processo ? ' — ' + p.numero_processo : '') + '</span>';
                h += '<span style="text-align:center">' + badge_dias + '</span>';
                h += '<span style="text-align:center"><span style="background:' + cor + '22;color:' + cor + ';padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + p.prioridade + '</span></span>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Tarefas
        if (d.tarefas.length) {
            h += secao('📋 Tarefas (' + d.tarefas.length + ')', '#2563eb');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            h += grid_header(['Tarefa','Serviço/Cliente','Status','Prazo','Prioridade'], '1.3fr 1fr 110px 110px 90px');
            d.tarefas.forEach(function(t) {
                var cor_p = t.prioridade === 'Urgente' ? '#dc2626' : t.prioridade === 'Alta' ? '#d97706' : '#6b7280';
                var cor_s = t.status === 'Em Andamento' ? '#2563eb' : '#d97706';

                var prazo_label = '';
                if (t.data_limite) {
                    var dias = t.dias_restantes;
                    if (dias !== null && dias !== undefined) {
                        if (dias < 0) prazo_label = '<span style="color:#dc2626;font-weight:600">Atrasada ' + Math.abs(dias) + 'd</span>';
                        else if (dias === 0) prazo_label = '<span style="color:#dc2626;font-weight:600">HOJE</span>';
                        else if (dias === 1) prazo_label = '<span style="color:#d97706">Amanhã</span>';
                        else prazo_label = '<span style="color:#6b7280">' + dias + ' dias</span>';
                    }
                    prazo_label += '<br><span style="font-size:10px;color:#9ca3af">' + fmt_data(t.data_limite) + '</span>';
                } else {
                    prazo_label = '<span style="color:#9ca3af;font-size:11px">Sem prazo</span>';
                }

                // Serviço/Cliente
                var ctx = '';
                if (t.cliente_nome) ctx = '<span style="font-weight:500;font-size:12px">' + t.cliente_nome + '</span>';
                if (t.servico_tipo) ctx += (ctx ? '<br>' : '') + '<span style="font-size:11px;color:#9ca3af">' + t.servico_tipo + '</span>';
                if (!ctx) ctx = '<span style="color:#9ca3af;font-size:11px">—</span>';

                h += '<div style="display:grid;grid-template-columns:1.3fr 1fr 110px 110px 90px;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Tarefa\',\'' + t.name + '\')">';
                h += '<span style="font-weight:500">' + (t.titulo || '') + '</span>';
                h += '<span>' + ctx + '</span>';
                h += '<span><span style="background:' + cor_s + '22;color:' + cor_s + ';padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + t.status + '</span></span>';
                h += '<span style="font-size:12px;text-align:center">' + prazo_label + '</span>';
                h += '<span style="text-align:center"><span style="background:' + cor_p + '22;color:' + cor_p + ';padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + t.prioridade + '</span></span>';
                h += '</div>';
            });
            h += '</div>';
        }

        if (!d.vencidas.length && !d.proximas.length && !d.repasses.length && !d.prazos.length && !d.tarefas.length && !(d.audiencias && d.audiencias.length)) {
            h += '<div style="text-align:center;padding:48px;color:#6b7280;background:#fff;border-radius:8px">✅ Nenhuma pendência no momento</div>';
        }

        root.innerHTML = h;
    }).catch(function(e) {
        root.innerHTML = '<p style="color:red">Erro ao carregar: ' + e + '</p>';
        console.error(e);
    });
}

function kpi(val, label, cor, scroll_id, count, list_dt) {
    var onclick = '';
    if (list_dt) {
        onclick = 'frappe.set_route(\'List\',\'' + list_dt + '\')';
    } else if (scroll_id) {
        onclick = 'scroll_to(\'' + scroll_id + '\')';
    }
    var badge = (count !== null && count !== undefined) ? '<span style="font-size:11px;color:#9ca3af;margin-left:4px">(' + count + ')</span>' : '';
    return '<div style="flex:1;min-width:130px;background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08);cursor:pointer;border-top:3px solid ' + cor + '" onclick="' + onclick + '">'
        + '<div style="font-size:22px;font-weight:700;color:' + cor + '">' + val + '</div>'
        + '<div style="font-size:12px;color:#6b7280;margin-top:4px">' + label + badge + '</div>'
        + '</div>';
}

function secao(titulo, cor) {
    return '<div style="font-size:14px;font-weight:600;color:' + cor + ';margin-bottom:8px;padding-left:4px">' + titulo + '</div>';
}

function grid_header(cols, template) {
    var h = '<div style="display:grid;grid-template-columns:' + template + ';padding:8px 16px;background:#f9fafb;font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;gap:8px">';
    cols.forEach(function(c) {
        h += '<span>' + c + '</span>';
    });
    h += '</div>';
    return h;
}

function tabela_parcelas(lista, cor, mostrar_atraso) {
    var cols = mostrar_atraso ? '1.5fr 1.2fr 1fr auto 70px' : '1.5fr 1.2fr 1fr auto';
    var h = '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';

    h += '<div style="display:grid;grid-template-columns:' + cols + ';padding:8px 16px;background:#f9fafb;font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;gap:8px">';
    h += '<span>Cliente</span><span>Serviço</span><span>Parcela</span><span style="text-align:right">Valor</span>';
    if (mostrar_atraso) h += '<span style="text-align:right">Atraso</span>';
    h += '</div>';

    lista.forEach(function(p) {
        var servico_label = p.servico_titulo || p.servico_tipo || p.servico_ref || '';
        if (p.numero_processo) {
            servico_label += ' <span style="font-size:10px;color:#9ca3af">' + p.numero_processo + '</span>';
        }

        h += '<div style="display:grid;grid-template-columns:' + cols + ';padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\'' + (p.parent || '') + '\')">';
        h += '<span style="font-weight:500">' + (p.cliente_nome || '-') + '</span>';
        h += '<span style="font-size:12px;color:#6b7280">' + servico_label + '</span>';

        var descricao = p['descrição'] || p.descricao || '';
        h += '<span style="font-size:12px"><span style="color:#374151">' + descricao + '</span><br>';
        h += '<span style="color:#9ca3af;font-size:11px">' + fmt_data(p.vencimento) + '</span></span>';
        h += '<span style="color:' + cor + ';font-weight:700;text-align:right;white-space:nowrap">' + fc(p.valor_total) + '</span>';

        if (mostrar_atraso) {
            var dias = p.dias_atraso || 0;
            var cor_atraso = dias > 30 ? '#dc2626' : dias > 7 ? '#d97706' : '#6b7280';
            h += '<span style="text-align:right;color:' + cor_atraso + ';font-size:12px;font-weight:600">' + dias + 'd</span>';
        }

        h += '</div>';
    });

    h += '</div>';
    return h;
}
