frappe.pages["painel"].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({parent: wrapper, title: "Painel do Escritorio", single_column: true});
    $(wrapper).find(".layout-main-section").html('<div id="painel-root" style="padding:15px"><div style="text-align:center;padding:60px">Carregando...</div></div>');
    var h0 = new Date().getHours();
    var gr = h0 < 12 ? "Bom dia" : h0 < 18 ? "Boa tarde" : "Boa noite";
    function fc(v){return "R$ "+(v||0).toLocaleString("pt-BR",{minimumFractionDigits:2});}
    function fd(d){if(!d)return "";var p=d.split("-");return p[2]+"/"+p[1]+"/"+p[0];}
    function du(d){if(!d)return 999;var t=new Date(d+"T00:00:00");var n=new Date();n.setHours(0,0,0,0);return Math.ceil((t-n)/86400000);}
    Promise.all([
        frappe.xcall("frappe.client.get_count",{doctype:"Servico",filters:{status:"Em andamento"}}),
        frappe.xcall("frappe.client.get_count",{doctype:"Acordo de Honorarios Processuais"}),
        frappe.xcall("frappe.client.get_list",{doctype:"Controle de Prazos",filters:{status:"Pendente",data_prazo:["<=",frappe.datetime.add_days(frappe.datetime.get_today(),7)]},fields:["name","servico","cliente","data_prazo","descricao","prioridade"],order_by:"data_prazo asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Audiencia",filters:{data_hora:[">=",frappe.datetime.get_today()]},fields:["name","servico","cliente","data_hora","tipo","modalidade","local_vara"],order_by:"data_hora asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Sales Invoice",filters:{docstatus:0,due_date:["<",frappe.datetime.get_today()],company:"Carine Pagel Advocacia"},fields:["name","customer","grand_total","due_date"],order_by:"due_date asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_list",{doctype:"Sales Invoice",filters:{docstatus:0,due_date:["between",[frappe.datetime.get_today(),frappe.datetime.add_days(frappe.datetime.get_today(),7)]],company:"Carine Pagel Advocacia"},fields:["name","customer","grand_total","due_date"],order_by:"due_date asc",limit_page_length:10}),
        frappe.xcall("frappe.client.get_count",{doctype:"Controle de Prazos",filters:{status:"Pendente"}})
    ]).then(function(r){
        var sv=r[0],ac=r[1],pz=r[2],au=r[3],fv=r[4],fs=r[5],tp=r[6];
        var tv=0;fv.forEach(function(f){tv+=f.grand_total;});
        var ts=0;fs.forEach(function(f){ts+=f.grand_total;});
        var h="<style>";
        h+="#painel-root{font-family:-apple-system,sans-serif;max-width:1200px;margin:0 auto}";
        h+=".p-head{padding:20px 0;border-bottom:1px solid var(--border-color)}";
        h+=".p-greet{font-size:22px;font-weight:600;color:var(--heading-color)}";
        h+=".kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;padding:20px 0}";
        h+=".kpi{background:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:16px;text-align:center;cursor:pointer}";
        h+=".kpi-val{font-size:28px;font-weight:700;color:var(--heading-color)}";
        h+=".kpi-lab{font-size:12px;color:var(--text-muted);margin-top:4px}";
        h+=".sg{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:10px 0}";
        h+=".sb{background:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:16px}";
        h+=".st{font-size:14px;font-weight:600;color:var(--heading-color);margin-bottom:12px;display:flex;align-items:center;gap:8px}";
        h+=".ri{padding:10px 0;border-bottom:1px solid var(--border-color);display:block;text-decoration:none;color:inherit}";
        h+=".ri:last-child{border-bottom:none}";
        h+=".rm{font-size:13px;font-weight:500;color:var(--heading-color)}";
        h+=".rs{font-size:11px;color:var(--text-muted);margin-top:2px}";
        h+=".rv{font-size:13px;font-weight:600;float:right}";
        h+=".br{background:#fee2e2;color:#dc2626;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}";
        h+=".bo{background:#fff7ed;color:#ea580c;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}";
        h+=".bg{background:#f0fdf4;color:#16a34a;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}";
        h+=".tb{padding:8px 12px;border-radius:6px;font-size:13px;font-weight:600;margin-top:8px;text-align:right}";
        h+=".em{padding:20px;text-align:center;color:var(--text-muted);font-size:12px}";
        h+=".vt{font-size:12px;color:var(--text-muted);cursor:pointer;margin-left:auto}";
        h+="@media(max-width:768px){.sg{grid-template-columns:1fr}.kpi-row{grid-template-columns:repeat(2,1fr)}}";
        h+="</style>";
        h+='<div class="p-head"><div class="p-greet">'+gr+', Carine</div></div>';
        h+='<div class="kpi-row">';
        h+='<div class="kpi" onclick="frappe.set_route(\'List\',\'Servico\',{status:\'Em andamento\'})"><div class="kpi-val">'+sv+'</div><div class="kpi-lab">Servicos Ativos</div></div>';
        h+='<div class="kpi" onclick="frappe.set_route(\'List\',\'Acordo de Honorarios Processuais\')"><div class="kpi-val">'+ac+'</div><div class="kpi-lab">Acordos</div></div>';
        h+='<div class="kpi" onclick="frappe.set_route(\'List\',\'Controle de Prazos\',{status:\'Pendente\'})"><div class="kpi-val">'+tp+'</div><div class="kpi-lab">Prazos Pendentes</div></div>';
        h+='<div class="kpi"><div class="kpi-val" style="color:#dc2626">'+fc(tv)+'</div><div class="kpi-lab">Faturas Vencidas</div></div>';
        h+='</div>';
        h+='<div class="sg"><div class="sb">';
        h+='<div class="st"><div style="width:4px;height:16px;border-radius:2px;background:#dc2626"></div>Prazos Urgentes<span class="vt" onclick="frappe.set_route(\'List\',\'Controle de Prazos\',{status:\'Pendente\'})">Ver todos</span></div>';
        if(pz.length===0){h+='<div class="em">Nenhum prazo nos proximos 7 dias</div>';}
        pz.forEach(function(p){var d=du(p.data_prazo);var b=d<0?"br":d<=1?"bo":"bg";var l=d<0?"Vencido ha "+Math.abs(d)+"d":d===0?"HOJE":d===1?"AMANHA":"em "+d+"d";h+='<a href="/app/controle-de-prazos/'+encodeURIComponent(p.name)+'" class="ri"><div class="rm">'+(p.descricao||p.name)+' <span class="'+b+'">'+l+'</span></div><div class="rs">'+(p.cliente||"")+' - '+fd(p.data_prazo)+'</div></a>';});
        h+='</div><div class="sb">';
        h+='<div class="st"><div style="width:4px;height:16px;border-radius:2px;background:#6366f1"></div>Proximas Audiencias<span class="vt" onclick="frappe.set_route(\'List\',\'Audiencia\')">Ver todos</span></div>';
        if(au.length===0){h+='<div class="em">Nenhuma audiencia agendada</div>';}
        au.forEach(function(a){var dd=a.data_hora?a.data_hora.split(" ")[0]:"";var ht=a.data_hora?a.data_hora.split(" ")[1]||"":"";var ic=a.modalidade==="Virtual"?"[V]":"[P]";h+='<a href="/app/audiencia/'+encodeURIComponent(a.name)+'" class="ri"><div class="rm">'+ic+' '+(a.tipo||"")+' - '+(a.cliente||"")+'</div><div class="rs">'+fd(dd)+' '+ht+' - '+(a.local_vara||"")+'</div></a>';});
        h+='</div></div>';
        h+='<div class="sg"><div class="sb">';
        h+='<div class="st"><div style="width:4px;height:16px;border-radius:2px;background:#dc2626"></div>Faturas Vencidas<span class="vt" onclick="frappe.set_route(\'List\',\'Sales Invoice\',{docstatus:0})">Ver todos</span></div>';
        if(fv.length===0){h+='<div class="em">Nenhuma fatura vencida</div>';}
        fv.forEach(function(f){var d=Math.abs(du(f.due_date));h+='<a href="/app/sales-invoice/'+encodeURIComponent(f.name)+'" class="ri"><div class="rm">'+f.customer+'<span class="rv" style="color:#dc2626">'+fc(f.grand_total)+'</span></div><div class="rs">'+f.name+' - venceu ha '+d+' dias</div></a>';});
        if(fv.length>0){h+='<div class="tb" style="background:#fee2e2;color:#dc2626">Total: '+fc(tv)+'</div>';}
        h+='</div><div class="sb">';
        h+='<div class="st"><div style="width:4px;height:16px;border-radius:2px;background:#f59e0b"></div>Vencem esta Semana<span class="vt" onclick="frappe.set_route(\'List\',\'Sales Invoice\',{docstatus:0})">Ver todos</span></div>';
        if(fs.length===0){h+='<div class="em">Nenhuma fatura vence esta semana</div>';}
        fs.forEach(function(f){var d=du(f.due_date);var l=d===0?"HOJE":d===1?"AMANHA":"em "+d+"d";h+='<a href="/app/sales-invoice/'+encodeURIComponent(f.name)+'" class="ri"><div class="rm">'+f.customer+'<span class="rv">'+fc(f.grand_total)+'</span></div><div class="rs">'+f.name+' - vence '+l+'</div></a>';});
        if(fs.length>0){h+='<div class="tb" style="background:#fff7ed;color:#ea580c">Total: '+fc(ts)+'</div>';}
        h+='</div></div>';
        h+='<div style="text-align:center;padding:20px;font-size:11px;color:var(--text-muted)">Carine Pagel Advocacia - Dados em tempo real</div>';
        document.getElementById("painel-root").innerHTML=h;
    }).catch(function(e){document.getElementById("painel-root").innerHTML='<div style="text-align:center;padding:40px;color:#dc2626">Erro: '+JSON.stringify(e)+'</div>';});
};
