frappe.pages['painel'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Painel Advocacia',
        single_column: true
    });

    page.add_button("+ Serviço",  function(){ frappe.new_doc("Servico"); },         {btn_class:"btn-default"});
    page.add_button("+ Cliente",  function(){ frappe.new_doc("Cliente"); },         {btn_class:"btn-default"});
    page.add_button("+ Fatura",   function(){ frappe.new_doc("Fatura"); },          {btn_class:"btn-default"});
    page.add_button("↺ Atualizar",function(){ render_painel(page); },               {btn_class:"btn-default"});

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
        // KPIs
        frappe.xcall("frappe.client.get_list", {
            doctype: "Fatura",
            filters: {status: "Vencida"},
            fields: ["name","valor","cliente"],
            order_by: "data_vencimento asc",
            limit_page_length: 50
        }),
        frappe.xcall("frappe.client.get_list", {
            doctype: "Fatura",
            filters: {status: "Pendente", data_vencimento: ["between", [hoje, set7]]},
            fields: ["name","valor","cliente","data_vencimento"],
            order_by: "data_vencimento asc",
            limit_page_length: 50
        }),
        frappe.xcall("frappe.client.get_list", {
            doctype: "Fatura",
            filters: {status: "Pendente", data_vencimento: [">", set7]},
            fields: ["name","valor"],
            limit_page_length: 0
        }),
        frappe.xcall("frappe.client.get_count", {doctype: "Cliente", filters: {}}),
        frappe.xcall("frappe.client.get_count", {doctype: "Servico", filters: {}}),
        frappe.xcall("frappe.client.get_list", {
            doctype: "Controle de Prazos",
            filters: {status: "Pendente", data_prazo: ["between", [hoje, set7]]},
            fields: ["name","descricao","data_prazo","prioridade"],
            order_by: "data_prazo asc",
            limit_page_length: 10
        })
    ]).then(function(r) {
        var vencidas = r[0], proximas = r[1], demais = r[2];
        var clientes = r[3], servicos = r[4], prazos = r[5];

        var total_vencido  = vencidas.reduce(function(s,f){ return s + (f.valor||0); }, 0);
        var total_proximos = proximas.reduce(function(s,f){ return s + (f.valor||0); }, 0);
        var total_futuro   = demais.reduce(function(s,f){ return s + (f.valor||0); }, 0);

        var h = '';

        // KPIs
        h += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px">';
        h += kpi(fc(total_vencido),  'Vencido',       '#dc2626', 'Fatura', {status:'Vencida'});
        h += kpi(fc(total_proximos), 'Vence em 7 dias','#d97706','Fatura', {status:'Pendente'});
        h += kpi(fc(total_futuro),   'A receber',      '#2563eb','Fatura', {status:'Pendente'});
        h += kpi(clientes,           'Clientes',       '#6b7280','Cliente',{});
        h += kpi(servicos,           'Serviços',       '#6b7280','Servico',{});
        h += '</div>';

        // Faturas vencidas
        if (vencidas.length) {
            h += secao('⚠️ Faturas Vencidas', '#dc2626');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            vencidas.forEach(function(f) {
                h += linha_fatura(f, '#dc2626');
            });
            h += '</div>';
        }

        // Vence esta semana
        if (proximas.length) {
            h += secao('📅 Vence nos Próximos 7 Dias', '#d97706');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            proximas.forEach(function(f) {
                h += linha_fatura(f, '#d97706');
            });
            h += '</div>';
        }

        // Prazos desta semana
        if (prazos.length) {
            h += secao('⏰ Prazos Esta Semana', '#7c3aed');
            h += '<div style="background:#fff;border-radius:8px;overflow:hidden;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">';
            prazos.forEach(function(p) {
                var cor = p.prioridade === 'Alta' ? '#dc2626' : p.prioridade === 'Media' ? '#d97706' : '#6b7280';
                h += '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Controle de Prazos\',\''+p.name+'\')">';
                h += '<span>'+p.descricao+'</span>';
                h += '<span style="color:'+cor+';font-weight:600">'+p.data_prazo+'</span>';
                h += '</div>';
            });
            h += '</div>';
        }

        if (!vencidas.length && !proximas.length && !prazos.length) {
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

function linha_fatura(f, cor) {
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f3f4f6;cursor:pointer" onclick="frappe.set_route(\'Form\',\'Fatura\',\''+f.name+'\')">'
        + '<span style="font-weight:500">'+f.cliente+'</span>'
        + '<span style="color:'+cor+';font-weight:700">'+fc(f.valor)+'</span>'
        + '</div>';
}
