frappe.pages["painel"].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Painel do Escritorio",
        single_column: true
    });
    page.menu_btn_group.hide();

    // Botoes visiveis no header — criacao rapida
    page.add_button("+ Servico",   function(){ frappe.new_doc("Servico"); },                   {btn_class:"btn-primary"});
    page.add_button("+ Cliente",   function(){ frappe.new_doc("Customer"); },                  {btn_class:"btn-default"});
    page.add_button("+ Prazo",     function(){ frappe.new_doc("Controle de Prazos"); },        {btn_class:"btn-default"});
    page.add_button("+ Audiencia", function(){ frappe.new_doc("Audiencia"); },                 {btn_class:"btn-default"});

    var root = $(wrapper).find(".layout-main-section");
    root.html('<div id="painel-root"><div style="text-align:center;padding:60px;color:var(--text-muted)">Carregando...</div></div>');

    function fc(v){ return "R$ "+(v||0).toLocaleString("pt-BR",{minimumFractionDigits:2}); }
    function fd(d){ if(!d) return ""; var p=d.split("-"); return p[2]+"/"+p[1]+"/"+p[0]; }
    function du(d){ if(!d) return 999; var t=new Date(d+"T00:00:00"); var n=new Date(); n.setHours(0,0,0,0); return Math.ceil((t-n)/86400000); }
    var h0 = new Date().getHours();
    var gr = h0<12?"Bom dia":h0<18?"Boa tarde":"Boa noite";

    Promise.all([
        frappe.xcall("frappe.client.get_count",{doctype:"Servico",filters:{status:"Em andamento"}}),
        frappe.xcall("frappe.client.get_count",{doctype:"Acordo de Honorarios Processuais"}),
        frappe.xcall("frappe.client.get_list",{doctype:"Controle de Prazos",filters:{status:"Pendente",data_prazo:["<=",frappe.datetime.add_days(frappe.datetime.get_today(),7)]},fields:["name","servico","cliente","data_prazo","descricao","prioridade"],order_by:"data_prazo asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Audiencia",filters:{data_hora:[">=",frappe.datetime.get_today()]},fields:["name","servico","cliente","data_hora","tipo","modalidade","local_vara","link_audiencia"],order_by:"data_hora asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Sales Invoice",filters:{docstatus:1,outstanding_amount:[">",0],due_date:["<",frappe.datetime.get_today()],company:"Carine Pagel Advocacia"},fields:["name","customer","grand_total","outstanding_amount","due_date"],order_by:"due_date asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Sales Invoice",filters:{docstatus:1,outstanding_amount:[">",0],due_date:["between",[frappe.datetime.get_today(),frappe.datetime.add_days(frappe.datetime.get_today(),7)]],company:"Carine Pagel Advocacia"},fields:["name","customer","grand_total","outstanding_amount","due_date"],order_by:"due_date asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_count",{doctype:"Controle de Prazos",filters:{status:"Pendente"}}),
        frappe.xcall("frappe.client.get_count",{doctype:"Customer",filters:{disabled:0}})
    ]).then(function(r){
        var sv=r[0], ac=r[1], pz=r[2], au=r[3], fv=r[4], fs=r[5], tp=r[6], cl=r[7];
        var tv=0; fv.forEach(function(f){ tv+=f.outstanding_amount; });
        var ts=0; fs.forEach(function(f){ ts+=f.outstanding_amount; });

        var h = "<style>";
        h += "#painel-root{font-family:-apple-system,sans-serif;max-width:1200px;margin:0 auto;padding:0 4px}";
        h += ".kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;padding:16px 0}";
        h += ".kpi{background:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:16px;text-align:center;cursor:pointer;transition:box-shadow .15s}";
        h += ".kpi:hover{box-shadow:0 2px 8px rgba(0,0,0,.1)}";
        h += ".kpi-val{font-size:26px;font-weight:700;color:var(--heading-color)}";
        h += ".kpi-lab{font-size:11px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}";
        h += ".sg{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}";
        h += ".sb{background:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:16px}";
        h += ".st{font-size:13px;font-weight:600;color:var(--heading-color);margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--border-color);display:flex;align-items:center;gap:6px}";
        h += ".ri{padding:8px 0;border-bottom:1px solid var(--border-color);display:block;color:inherit;cursor:pointer}";
        h += ".ri:hover{background:var(--fg-hover-color);margin:0 -8px;padding:8px}";
        h += ".ri:last-child{border-bottom:none}";
        h += ".rm{font-size:13px;font-weight:500;color:var(--heading-color)}";
        h += ".rs{font-size:11px;color:var(--text-muted);margin-top:2px}";
        h += ".rv{font-size:12px;font-weight:600;float:right;margin-top:2px}";
        h += ".tag-r{background:#fee2e2;color:#dc2626;padding:1px 6px;border-radius:8px;font-size:10px;font-weight:600}";
        h += ".tag-o{background:#fff7ed;color:#ea580c;padding:1px 6px;border-radius:8px;font-size:10px;font-weight:600}";
        h += ".tag-g{background:#f0fdf4;color:#16a34a;padding:1px 6px;border-radius:8px;font-size:10px;font-weight:600}";
        h += ".total-bar{padding:8px;border-radius:6px;font-size:12px;font-weight:600;margin-top:8px;text-align:right}";
        h += ".em{padding:20px;text-align:center;color:var(--text-muted);font-size:12px}";
        h += ".sec-link{font-size:11px;color:var(--text-muted);cursor:pointer;margin-left:auto;font-weight:400}";
        h += ".sec-link:hover{color:var(--primary)}";
        h += "@media(max-width:768px){.sg{grid-template-columns:1fr}.kpi-row{grid-template-columns:repeat(2,1fr)}}";
        h += "</style>";

        // KPIs — 5 cards
        h += '<div class="kpi-row">';
        h += '<div class="kpi" onclick="frappe.set_route(\'List\',\'Servico\',{status:\'Em andamento\'})"><div class="kpi-val">'+sv+'</div><div class="kpi-lab">Servicos Ativos</div></div>';
        h += '<div class="kpi" onclick="frappe.set_route(\'List\',\'Acordo de Honorarios Processuais\')"><div class="kpi-val">'+ac+'</div><div class="kpi-lab">Acordos</div></div>';
        h += '<div class="kpi" onclick="frappe.set_route(\'List\',\'Controle de Prazos\',{status:\'Pendente\'})"><div class="kpi-val">'+tp+'</div><div class="kpi-lab">Prazos Pendentes</div></div>';
        h += '<div class="kpi" onclick="frappe.set_route(\'List\',\'Sales Invoice\',{docstatus:\'1\'})"><div class="kpi-val" style="color:#dc2626">'+fc(tv)+'</div><div class="kpi-lab">Faturas Vencidas</div></div>';
        h += '<div class="kpi" onclick="frappe.set_route(\'List\',\'Customer\')"><div class="kpi-val">'+cl+'</div><div class="kpi-lab">Clientes</div></div>';
        h += '</div>';

        // Prazos + Audiencias
        h += '<div class="sg">';
        h += '<div class="sb"><div class="st">Prazos Urgentes <span class="sec-link" onclick="frappe.set_route(\'List\',\'Controle de Prazos\',{status:\'Pendente\'})">Ver todos</span></div>';
        if(pz.length===0){ h += '<div class="em">Nenhum prazo nos proximos 7 dias</div>'; }
        pz.forEach(function(p){
            var d = du(p.data_prazo);
            var tag = d<0?'<span class="tag-r">VENCIDO</span>':d===0?'<span class="tag-r">HOJE</span>':d===1?'<span class="tag-o">AMANHA</span>':'<span class="tag-o">'+d+' dias</span>';
            h += '<div class="ri" onclick="frappe.set_route(\'Form\',\'Controle de Prazos\',\''+p.name+'\')">';
            h += '<div class="rm">'+tag+' '+(p.descricao||p.name)+'</div>';
            h += '<div class="rs">'+(p.cliente||'')+(p.data_prazo?' - '+fd(p.data_prazo):'')+'</div></div>';
        });
        h += '</div>';

        h += '<div class="sb"><div class="st">Proximas Audiencias <span class="sec-link" onclick="frappe.set_route(\'List\',\'Audiencia\')">Ver todas</span></div>';
        if(au.length===0){ h += '<div class="em">Nenhuma audiencia agendada</div>'; }
        au.forEach(function(a){
            var d = a.data_hora ? a.data_hora.split(" ")[0] : "";
            var hr = a.data_hora && a.data_hora.split(" ")[1] ? a.data_hora.split(" ")[1].substring(0,5) : "";
            var dd = du(d);
            var tag = dd===0?'<span class="tag-r">HOJE '+hr+'</span>':dd===1?'<span class="tag-o">AMANHA '+hr+'</span>':'<span class="tag-g">'+fd(d)+' '+hr+'</span>';
            var ic = a.modalidade==="Virtual" ? "[V]" : "[P]";
            var entrar = (a.modalidade==="Virtual" && a.link_audiencia) ? '<a href="'+a.link_audiencia+'" target="_blank" style="margin-left:8px;background:#16a34a;color:#fff;padding:2px 10px;border-radius:8px;font-size:11px;font-weight:600;text-decoration:none">Entrar</a>' : '';
            h += '<div class="ri" onclick="frappe.set_route(\'Form\',\'Audiencia\',\''+a.name+'\')">';
            h += '<div class="rm">'+tag+' '+ic+' '+(a.tipo||'')+'</div>';
            h += '<div class="rs">'+(a.cliente||'')+(a.local_vara?' - '+a.local_vara:'')+entrar+'</div></div>';
        });
        h += '</div></div>';

        // Faturas vencidas + semana
        h += '<div class="sg">';
        h += '<div class="sb"><div class="st">Faturas Vencidas <span class="sec-link" onclick="frappe.set_route(\'List\',\'Sales Invoice\',{docstatus:\'1\'})">Ver todas</span></div>';
        if(fv.length===0){ h += '<div class="em">Nenhuma fatura vencida</div>'; }
        fv.forEach(function(f){
            var d = -du(f.due_date);
            h += '<div class="ri" onclick="frappe.set_route(\'Form\',\'Sales Invoice\',\''+f.name+'\')">';
            h += '<div class="rm">'+f.customer+'<span class="rv" style="color:#dc2626">'+fc(f.outstanding_amount)+'</span></div>';
            h += '<div class="rs">'+f.name+' - Venc. '+fd(f.due_date)+' <span class="tag-r">'+d+' dias atraso</span></div></div>';
        });
        if(fv.length>0){ h += '<div class="total-bar" style="background:#fee2e2;color:#dc2626">Total vencido: '+fc(tv)+'</div>'; }
        h += '</div>';

        h += '<div class="sb"><div class="st">Vencem Esta Semana <span class="sec-link" onclick="frappe.set_route(\'List\',\'Sales Invoice\',{docstatus:\'1\'})">Ver todas</span></div>';
        if(fs.length===0){ h += '<div class="em">Nenhuma fatura vence nos proximos 7 dias</div>'; }
        fs.forEach(function(f){
            var d = du(f.due_date);
            h += '<div class="ri" onclick="frappe.set_route(\'Form\',\'Sales Invoice\',\''+f.name+'\')">';
            h += '<div class="rm">'+f.customer+'<span class="rv">'+fc(f.outstanding_amount)+'</span></div>';
            h += '<div class="rs">'+f.name+' - Venc. '+fd(f.due_date)+' <span class="tag-o">em '+d+' dias</span></div></div>';
        });
        if(fs.length>0){ h += '<div class="total-bar" style="background:#fff7ed;color:#ea580c">Total a vencer: '+fc(ts)+'</div>'; }
        h += '</div></div>';

        document.getElementById("painel-root").innerHTML = h;

    }).catch(function(err){
        document.getElementById("painel-root").innerHTML = '<div style="padding:40px;text-align:center;color:#dc2626">Erro: '+JSON.stringify(err)+'</div>';
    });
};
