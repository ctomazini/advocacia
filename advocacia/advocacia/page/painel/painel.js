frappe.pages['painel'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Painel Advocacia',
        single_column: true
    });

    page.add_button("+ Serviço",   function(){ frappe.new_doc("Servico"); },          {btn_class:"btn-default"});
    page.add_button("+ Cliente",   function(){ frappe.new_doc("Cliente"); },          {btn_class:"btn-default"});
    page.add_button("+ Tarefa",    function(){ frappe.new_doc("Tarefa"); },           {btn_class:"btn-default"});
    page.add_button("↺ Atualizar", function(){ render_painel(page); },                {btn_class:"btn-default"});

    $(wrapper).find('.page-content').html('<div id="painel-root" style="padding:20px"></div>');
    render_painel(page);
};

function fc(v) {
    return 'R$ ' + parseFloat(v||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function render_painel(page) {
    var root = document.getElementById('painel-root');
    root.innerHTML = '<p style="color:#888">Carregando...</p>';

    var hoje = frappe.datetime.get_today();
    var set7 = frappe.datetime.add_days(hoje, 7);

    Promise.all([
        // Parcelas vencidas
        frappe.xcall("frappe.client.get_list", {
            doctype: "Parcela de Honorarios",
            filters: {status: "Vencida"},
            fields: ["name","valor_total","valor_advogada","valor_cliente","vencimento","parent"],
            order_by: "vencimento asc",
            limit_page_length: 50
        }),
        // Parcelas a vencer em 7 dias
        frappe.xcall("frappe.client.get_list", {
            doctype: "Parcela de Honorarios",
            filters: {status: "Pendente", vencimento: ["between", [hoje, set7]]},
            fields: ["name","valor_total","valor_advogada","valor_cliente","vencimento","parent"],
            order_by: "vencimento asc",
            limit_page_length: 50
        }),
        // Repasses pendentes (recebido mas não repassado)
        frappe.xcall("frappe.client.get_list", {
            doctype: "Parcela de Honorarios",
            filters: {status: "Recebida", valor_cliente: [">", 0]},
            fields: ["name","valor_cliente","vencimento","parent"],
            order_by: "vencimento asc",
            limit_page_length: 20
        }),
        // KPI total a receber (pendentes futuras)
        frappe.xcall("frappe.client.get_list", {
            doctype: "Parcela de Honorarios",
            filters: {status: "Pendente", vencimento: [">", set7]},
            fields: ["valor_advogada"],
            limit_page_length: 0
        }),
        // Clientes e Serviços
        frappe.xcall("frappe.client.get_count", {doctype: "Cliente", filters: {}}),
        frappe.xcall("frappe.client.get_count", {doctype: "Servico", filters: {}}),
        // Prazos desta semana
        frappe.xcall("frappe.client.get_list", {
            doctype: "Controle de Prazos",
            filters: {status: "Pendente", data_prazo: ["between", [hoje, set7]]},
            fields: ["name","descricao","data_prazo","prioridade"],
            order_by: "data_prazo asc",
            limit_page_length: 10
        }),
        // Tarefas pendentes
        frappe.xcall("frappe.client.get_list", {
            doctype: "Tarefa",
            filters: {status: ["in", ["Pendente", "Em Andamento"]]},
            fields: ["name","titulo","status","prioridade","data_limite"],
            order_by: "prioridade desc, data_limite asc",
            limit_page_length: 10
        })
    ]).then(function(r) {
        var vencidas = r[0], proximas = r[1], repasses = r[2], futuras = r[3];
        var clientes = r[4], servicos = r[5], prazos = r[6], tarefas = r[7];

        var total_vencido  = vencidas.reduce(function(s,p){ return s+(p.valor_advogada||0);},0);
        var total_proximos = proximas.reduce(function(s,p){ return s+(p.valor_advogada||0);},0);
        var total_futuro   = futuras.reduce(function(s,p){ return s+(p.valor_advogada||0);},0);
        var total_repasse  = repasses.reduce(function(s,p){ return s+(p.valor_cliente||0);},0);

        var h = '';

        // KPIs
        h += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px">';
        h += kpi(fc(total_vencido),  'Vencido (Carine)',    '#dc2626', 'Parcela de Honorarios', {status:'Vencida'});
        h += kpi(fc(total_proximos), 'Vence em 7 dias',     '#d97706', 'Parcela de Honorarios', {status:'Pendente'});
        h += kpi(fc(total_futuro),   'A receber (futuro)',  '#2563eb', 'Parcela de Honorarios', {status:'Pendente'});
        h += kpi(fc(total_repasse),  'Repasse ao cliente',  '#7c3aed', 'Parcela de Honorarios', {status:'Recebida'});
        h += kpi(clientes,           'Clientes',            '#6b7280', 'Cliente', {});
        h += kpi(servicos,           'Serviços',            '#6b7280', 'Servico', {});
        h += '</div>';

        // Parcelas vencidas
        if (vencidas.length) {
            h += secao('⚠️ Honorários Vencidos', '#dc2626');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            vencidas.forEach(function(p) {
                h += linha_parcela(p, '#dc2626');
            });
            h += '</div>';
        }

        // Vence esta semana
        if (proximas.length) {
            h += secao('📅 Vence nos Próximos 7 Dias', '#d97706');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            proximas.forEach(function(p) {
                h += linha_parcela(p, '#d97706');
            });
            h += '</div>';
        }

        // Repasses pendentes
        if (repasses.length) {
            h += secao('↗ Repasses Pendentes ao Cliente', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            repasses.forEach(function(p) {
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\''+p.parent+'\')">';
                h += '<span>Acordo: '+p.parent+'</span>';
                h += '<span style="color:#7c3aed;font-weight:700">'+fc(p.valor_cliente)+'</span>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Prazos desta semana
        if (prazos.length) {
            h += secao('⏰ Prazos Esta Semana', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            prazos.forEach(function(p) {
                var cor = p.prioridade==='Alta'?'#dc2626':p.prioridade==='Media'?'#d97706':'#6b7280';
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Controle de Prazos\',\''+p.name+'\')">';
                h += '<span>'+p.descricao+'</span>';
                h += '<span style="color:'+cor+';font-weight:600">'+p.data_prazo+'</span>';
                h += '</div>';
            });
            h += '</div>';
        }

        // Tarefas pendentes
        if (tarefas.length) {
            h += secao('📋 Tarefas', '#2563eb');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            tarefas.forEach(function(t) {
                var cor_p = t.prioridade==='Urgente'?'#dc2626':t.prioridade==='Alta'?'#d97706':'#6b7280';
                var cor_s = t.status==='Em Andamento'?'#2563eb':'#d97706';
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Tarefa\',\''+t.name+'\')">';
                h += '<div><span style="font-weight:500">'+t.titulo+'</span> <span style="font-size:11px;color:'+cor_p+'">'+t.prioridade+'</span></div>';
                h += '<div><span style="color:'+cor_s+';font-size:12px">'+t.status+'</span>'+(t.data_limite?'<span style="color:#6b7280;font-size:11px;margin-left:8px">'+t.data_limite+'</span>':'')+'</div>';
                h += '</div>';
            });
            h += '</div>';
        }

        if (!vencidas.length && !proximas.length && !repasses.length && !prazos.length && !tarefas.length) {
            h += '<div style="text-align:center;padding:48px;color:#6b7280;background:#fff;border-radius:8px">✅ Nenhuma pendência no momento</div>';
        }

        root.innerHTML = h;
    }).catch(function(e) {
        root.innerHTML = '<p style="color:red">Erro ao carregar: ' + e + '</p>';
    });
}

function kpi(val, label, cor, dt, filters) {
    return '<div style="flex:1;min-width:140px;background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08);cursor:pointer;border-top:3px solid '+cor+'" onclick="frappe.set_route(\'List\',\''+dt+'\','+JSON.stringify(filters)+')">'
        + '<div style="font-size:22px;font-weight:700;color:'+cor+'">'+val+'</div>'
        + '<div style="font-size:12px;color:#6b7280;margin-top:4px">'+label+'</div>'
        + '</div>';
}

function secao(titulo, cor) {
    return '<div style="font-size:14px;font-weight:600;color:'+cor+';margin-bottom:8px;padding-left:4px">'+titulo+'</div>';
}

function linha_parcela(p, cor) {
    var label = p.parent || p.name;
    var extra = p.valor_cliente > 0 ? ' <span style="font-size:11px;color:#7c3aed">(+'+fc(p.valor_cliente)+' cliente)</span>' : '';
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Acordo de Honorarios Processuais\',\''+p.parent+'\')">'
        + '<span style="font-weight:500">'+label+extra+'</span>'
        + '<div><span style="color:'+cor+';font-weight:700">'+fc(p.valor_advogada)+'</span>'
        + '<span style="color:#9ca3af;font-size:11px;margin-left:8px">'+p.vencimento+'</span></div>'
        + '</div>';
}
