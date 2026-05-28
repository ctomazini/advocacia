frappe.pages['painel'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Painel Advocacia',
        single_column: true
    });

    page.add_button("+ Serviço",   function(){ frappe.new_doc("Servico"); },   {btn_class:"btn-default"});
    page.add_button("+ Cliente",   function(){ frappe.new_doc("Cliente"); },   {btn_class:"btn-default"});
    page.add_button("+ Tarefa",    function(){ frappe.new_doc("Tarefa"); },    {btn_class:"btn-default"});
    page.add_button("↺ Atualizar", function(){ render_painel(page); },         {btn_class:"btn-default"});

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

function render_painel(page) {
    var root = document.getElementById('painel-root');
    root.innerHTML = '<p style="color:#888">Carregando...</p>';

    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data").then(function(d) {
        var t = d.totais;
        var h = '';

        // KPIs
        h += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px">';
        h += kpi(fc(t.vencido),   'Vencido',            '#dc2626', 'Parcela de Honorarios', {status:'Vencida'});
        h += kpi(fc(t.proximos),  'Vence em 7 dias',    '#d97706', 'Parcela de Honorarios', {status:'Pendente'});
        h += kpi(fc(t.futuro),    'A receber (futuro)', '#2563eb', 'Parcela de Honorarios', {status:'Pendente'});
        h += kpi(fc(t.repasse),   'Repasse pendente',   '#7c3aed', 'Parcela de Honorarios', {status:'Recebida'});
        h += kpi(d.clientes,      'Clientes',           '#6b7280', 'Cliente', {});
        h += kpi(d.servicos,      'Serviços',           '#6b7280', 'Servico', {});
        h += '</div>';

        // Vencidas
        if (d.vencidas.length) {
            h += secao('⚠️ Honorários Vencidos (' + d.vencidas.length + ')', '#dc2626');
            h += tabela_parcelas(d.vencidas, '#dc2626', true);
        }

        // Próximos 7 dias
        if (d.proximas.length) {
            h += secao('📅 Vence nos Próximos 7 Dias (' + d.proximas.length + ')', '#d97706');
            h += tabela_parcelas(d.proximas, '#d97706', false);
        }

        // Repasses
        if (d.repasses.length) {
            h += secao('↗ Repasses Pendentes (' + d.repasses.length + ')', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            h += grid_header(['Cliente','Serviço','Valor Cliente'], '1fr 1fr auto');
            d.repasses.forEach(function(p) {
                h += '<div style="display:grid;grid-template-columns:1fr 1fr auto;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\'' + p.parent + '\')">';
                h += '<span style="font-weight:500">' + (p.cliente_nome || '-') + '</span>';
                h += '<span style="color:#6b7280;font-size:12px">' + (p.servico_titulo || p.servico_ref || '') + '</span>';
                h += '<span style="color:#7c3aed;font-weight:700;text-align:right">' + fc(p.valor_cliente) + '</span>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Prazos
        if (d.prazos.length) {
            h += secao('⏰ Prazos Esta Semana (' + d.prazos.length + ')', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            d.prazos.forEach(function(p) {
                var cor = p.prioridade === 'Alta' ? '#dc2626' : p.prioridade === 'Media' ? '#d97706' : '#6b7280';
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Controle de Prazos\',\'' + p.name + '\')">';
                h += '<div><span style="font-weight:500">' + p.descricao + '</span>';
                if (p.cliente_nome) h += ' <span style="font-size:11px;color:#9ca3af">— ' + p.cliente_nome + '</span>';
                h += '</div>';
                h += '<div><span style="background:' + cor + '22;color:' + cor + ';padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + p.prioridade + '</span>';
                h += '<span style="color:#6b7280;font-size:12px;margin-left:8px">' + fmt_data(p.data_prazo) + '</span></div>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Tarefas
        if (d.tarefas.length) {
            h += secao('📋 Tarefas (' + d.tarefas.length + ')', '#2563eb');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            d.tarefas.forEach(function(t) {
                var cor_p = t.prioridade === 'Urgente' ? '#dc2626' : t.prioridade === 'Alta' ? '#d97706' : '#6b7280';
                var cor_s = t.status === 'Em Andamento' ? '#2563eb' : '#d97706';
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Tarefa\',\'' + t.name + '\')">';
                h += '<div><span style="font-weight:500">' + t.titulo + '</span> ';
                h += '<span style="background:' + cor_p + '22;color:' + cor_p + ';padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">' + t.prioridade + '</span></div>';
                h += '<div><span style="color:' + cor_s + ';font-size:12px;font-weight:500">' + t.status + '</span>';
                if (t.data_limite) h += '<span style="color:#6b7280;font-size:11px;margin-left:8px">' + fmt_data(t.data_limite) + '</span>';
                h += '</div>';
                h += '</div>';
            });
            h += '</div>';
        }

        if (!d.vencidas.length && !d.proximas.length && !d.repasses.length && !d.prazos.length && !d.tarefas.length) {
            h += '<div style="text-align:center;padding:48px;color:#6b7280;background:#fff;border-radius:8px">✅ Nenhuma pendência no momento</div>';
        }

        root.innerHTML = h;
    }).catch(function(e) {
        root.innerHTML = '<p style="color:red">Erro ao carregar: ' + e + '</p>';
        console.error(e);
    });
}

function kpi(val, label, cor, dt, filters) {
    return '<div style="flex:1;min-width:130px;background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08);cursor:pointer;border-top:3px solid ' + cor + '" onclick="frappe.set_route(\'List\',\'' + dt + '\',' + JSON.stringify(filters) + ')">'
        + '<div style="font-size:22px;font-weight:700;color:' + cor + '">' + val + '</div>'
        + '<div style="font-size:12px;color:#6b7280;margin-top:4px">' + label + '</div>'
        + '</div>';
}

function secao(titulo, cor) {
    return '<div style="font-size:14px;font-weight:600;color:' + cor + ';margin-bottom:8px;padding-left:4px">' + titulo + '</div>';
}

function grid_header(cols, template) {
    var h = '<div style="display:grid;grid-template-columns:' + template + ';padding:8px 16px;background:#f9fafb;font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase">';
    cols.forEach(function(c, i) {
        var align = i === cols.length - 1 ? 'text-align:right' : '';
        h += '<span style="' + align + '">' + c + '</span>';
    });
    h += '</div>';
    return h;
}

function tabela_parcelas(lista, cor, mostrar_atraso) {
    var cols = mostrar_atraso ? '1.5fr 1.2fr 1fr auto 70px' : '1.5fr 1.2fr 1fr auto';
    var h = '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';

    // Header
    h += '<div style="display:grid;grid-template-columns:' + cols + ';padding:8px 16px;background:#f9fafb;font-size:11px;color:#6b7280;font-weight:600;text-transform:uppercase;gap:8px">';
    h += '<span>Cliente</span><span>Serviço</span><span>Parcela</span><span style="text-align:right">Valor</span>';
    if (mostrar_atraso) h += '<span style="text-align:right">Atraso</span>';
    h += '</div>';

    // Rows
    lista.forEach(function(p) {
        var servico_label = p.servico_titulo || p.servico_tipo || p.servico_ref || '';
        if (p.numero_processo) {
            servico_label += ' <span style="font-size:10px;color:#9ca3af">' + p.numero_processo + '</span>';
        }

        h += '<div style="display:grid;grid-template-columns:' + cols + ';padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer;align-items:center;gap:8px" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\'' + (p.parent || '') + '\')">';

        // Cliente
        h += '<span style="font-weight:500">' + (p.cliente_nome || '-') + '</span>';

        // Serviço
        h += '<span style="font-size:12px;color:#6b7280">' + servico_label + '</span>';

        // Parcela + vencimento
        var descricao = p['descrição'] || p.descricao || '';
        h += '<span style="font-size:12px"><span style="color:#374151">' + descricao + '</span><br>';
        h += '<span style="color:#9ca3af;font-size:11px">' + fmt_data(p.vencimento) + '</span></span>';

        // Valor
        h += '<span style="color:' + cor + ';font-weight:700;text-align:right;white-space:nowrap">' + fc(p.valor_total) + '</span>';

        // Atraso
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
