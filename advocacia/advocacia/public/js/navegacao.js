(function() {
    var FAB_ID = "fab-painel-global";
    var DTS = ["Servico","Controle de Prazos","Audiencia","Registro de Atos","Acordo de Honorarios Processuais","Tarefa","Cliente","Template Documento"];

    function addFab() {
        if(document.getElementById(FAB_ID)) return;
        var b = document.createElement("button");
        b.id = FAB_ID;
        b.innerHTML = "&#8592; Painel";
        b.style.cssText = "position:fixed;bottom:28px;right:28px;background:var(--primary);color:#fff;border:none;border-radius:50px;padding:10px 20px;font-size:13px;font-weight:600;cursor:pointer;display:none;box-shadow:0 4px 12px rgba(0,0,0,.25);z-index:9999";
        b.onclick = function(){ frappe.set_route("painel"); };
        document.body.appendChild(b);
    }

    function showFab(show) {
        var fab = document.getElementById(FAB_ID);
        if(fab) fab.style.display = show ? "block" : "none";
    }

    function addHeaderBtn(frm) {
        if(frm.page.__painel_btn) return;
        frm.page.add_button("Painel", function(){ frappe.set_route("painel"); }, {btn_class:"btn-default"});
        frm.page.__painel_btn = true;
    }

    frappe.after_ajax(function() {
        addFab();
        var route = frappe.get_route();
        var inScope = route && (route[0]==="Form"||route[0]==="List") && DTS.indexOf(route[1])>-1;
        showFab(!!inScope);
    });

    $(document).on("page-change", function() {
        var route = frappe.get_route();
        var inScope = route && (route[0]==="Form"||route[0]==="List") && DTS.indexOf(route[1])>-1;
        addFab();
        showFab(!!inScope);
    });

    DTS.forEach(function(dt) {
        frappe.ui.form.on(dt, {
            refresh: function(frm) {
                addHeaderBtn(frm);
                addFab();
                showFab(true);
            }
        });
    });

    frappe.views.calendar["Audiencia"] = {
        field_map: { start:"data_hora", end:"data_hora", id:"name", title:"tipo", allDay:false },
        get_css_class: function(d){ return d.modalidade==="Virtual"?"green":"blue"; }
    };
    frappe.views.calendar["Controle de Prazos"] = {
        field_map: { start:"data_prazo", end:"data_prazo", id:"name", title:"descricao", allDay:true },
        get_css_class: function(d){ return d.prioridade==="Alta"?"red":d.prioridade==="Media"?"orange":"blue"; }
    };
})();
