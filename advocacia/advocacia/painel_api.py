import frappe
from frappe.utils import today, add_days, date_diff

@frappe.whitelist()
def get_painel_data():
    hoje = today()
    set7 = add_days(hoje, 7)

    def enriquecer_parcelas(parcelas):
        """Adiciona dados do Acordo, Cliente e Serviço a cada parcela."""
        cache_acordo = {}
        for p in parcelas:
            acordo_name = p.get("parent")
            if not acordo_name:
                continue
            if acordo_name not in cache_acordo:
                try:
                    a = frappe.db.get_value("Acordo de Honorarios Processuais", acordo_name,
                        ["cliente","servico","modo_honorarios","valor_total_do_acordo"], as_dict=True)
                    if a and a.servico:
                        s = frappe.db.get_value("Servico", a.servico,
                            ["title","tipo","numero_processo","area","comarca"], as_dict=True)
                        a.update({"serv_" + k: v for k, v in (s or {}).items()})
                    cache_acordo[acordo_name] = a or {}
                except Exception:
                    cache_acordo[acordo_name] = {}

            info = cache_acordo[acordo_name]
            p["cliente_nome"] = info.get("cliente", "")
            p["servico_ref"] = info.get("servico", "")
            p["servico_titulo"] = info.get("serv_title", "")
            p["servico_tipo"] = info.get("serv_tipo", "")
            p["numero_processo"] = info.get("serv_numero_processo", "")
            p["modo"] = info.get("modo_honorarios", "")
            p["dias_atraso"] = date_diff(hoje, p.get("vencimento")) if p.get("vencimento") else 0
            p["dias_para_vencer"] = date_diff(p.get("vencimento"), hoje) if p.get("vencimento") else 0
        return parcelas

    base_fields = ["name","parent","valor_total","valor_advogada","valor_cliente",
                    "vencimento","status","`descrição`"]

    vencidas = enriquecer_parcelas(frappe.get_all("Parcela de Honorarios",
        filters={"status": "Vencida"},
        fields=base_fields, order_by="vencimento asc", limit_page_length=50))

    proximas = enriquecer_parcelas(frappe.get_all("Parcela de Honorarios",
        filters={"status": "Pendente", "vencimento": ["between", [hoje, set7]]},
        fields=base_fields, order_by="vencimento asc", limit_page_length=50))

    repasses = enriquecer_parcelas(frappe.get_all("Parcela de Honorarios",
        filters={"status": "Recebida", "valor_cliente": [">", 0]},
        fields=base_fields, order_by="vencimento asc", limit_page_length=20))

    futuras = frappe.get_all("Parcela de Honorarios",
        filters={"status": "Pendente", "vencimento": [">", set7]},
        fields=["valor_total","valor_advogada"], limit_page_length=0)

    prazos = frappe.get_all("Controle de Prazos",
        filters={"status": "Pendente", "data_prazo": ["between", [hoje, set7]]},
        fields=["name","descricao","data_prazo","prioridade","servico"],
        order_by="data_prazo asc", limit_page_length=10)
    for p in prazos:
        if p.get("servico"):
            cli = frappe.db.get_value("Servico", p.servico, "cliente")
            p["cliente_nome"] = cli or ""

    tarefas = frappe.get_all("Tarefa",
        filters={"status": ["in", ["Pendente", "Em Andamento"]]},
        fields=["name","titulo","status","prioridade","data_limite"],
        order_by="prioridade desc, data_limite asc", limit_page_length=10)

    clientes = frappe.db.count("Cliente")
    servicos = frappe.db.count("Servico")

    total_vencido = sum(p.get("valor_total", 0) for p in vencidas)
    total_proximos = sum(p.get("valor_total", 0) for p in proximas)
    total_futuro = sum(p.get("valor_total", 0) for p in futuras)
    total_repasse = sum(p.get("valor_cliente", 0) for p in repasses)

    return {
        "vencidas": vencidas, "proximas": proximas,
        "repasses": repasses, "futuras": futuras,
        "prazos": prazos, "tarefas": tarefas,
        "clientes": clientes, "servicos": servicos,
        "totais": {
            "vencido": total_vencido, "proximos": total_proximos,
            "futuro": total_futuro, "repasse": total_repasse
        }
    }
