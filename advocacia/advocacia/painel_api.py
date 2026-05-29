import frappe
from frappe import _
from frappe.utils import (
    add_days,
    cint,
    date_diff,
    flt,
    get_first_day,
    get_last_day,
    today,
)


PARCELA_FIELDS = [
    "name",
    "parent",
    "valor_total",
    "valor_advogada",
    "valor_cliente",
    "vencimento",
    "status",
    "descrição",
]


@frappe.whitelist()
def get_painel_data(limit_start=0, limit_page_length=20):
    if not frappe.has_permission("Servico", "read"):
        frappe.throw(_("Sem permissão"), frappe.PermissionError)

    limit_start = cint(limit_start)
    limit_page_length = min(cint(limit_page_length or 20), 100)

    hoje = today()
    sete_dias = add_days(hoje, 7)
    trinta_dias = add_days(hoje, 30)
    mes_inicio = get_first_day(hoje)
    mes_fim = get_last_day(hoje)

    kpis = _build_kpis(hoje, sete_dias, trinta_dias, mes_inicio, mes_fim)
    alertas = _build_alertas(hoje, sete_dias)
    parcelas = _get_parcelas(hoje, limit_start, limit_page_length)
    audiencias = _get_audiencias(hoje, sete_dias)
    prazos = _get_prazos(hoje, sete_dias)
    tarefas = _get_tarefas(hoje, limit_start, limit_page_length)

    return {
        "kpis": kpis,
        "alertas": alertas,
        "parcelas": parcelas,
        "audiencias": audiencias,
        "prazos": prazos,
        "tarefas": tarefas,
    }


def _build_kpis(hoje, sete_dias, trinta_dias, mes_inicio, mes_fim):
    vencidas = frappe.get_all(
        "Parcela de Honorarios",
        filters={"status": "Vencida"},
        fields=["valor_total"],
        limit_page_length=500,
    )
    a_vencer = frappe.get_all(
        "Parcela de Honorarios",
        filters={
            "status": "Pendente",
            "vencimento": ["between", [hoje, trinta_dias]],
        },
        fields=["valor_total"],
        limit_page_length=500,
    )
    recebidas_mes = frappe.get_all(
        "Parcela de Honorarios",
        filters={
            "status": ["in", ["Recebida", "Repassada"]],
            "data_recebimento": ["between", [mes_inicio, mes_fim]],
        },
        fields=["valor_total"],
        limit_page_length=500,
    )

    return {
        "total_clientes": frappe.db.count("Cliente"),
        "servicos_ativos": frappe.db.count("Servico", {"status": "Em andamento"}),
        "parcelas_vencidas": {
            "count": len(vencidas),
            "valor": sum(flt(p.valor_total) for p in vencidas),
        },
        "parcelas_a_vencer_30d": {
            "count": len(a_vencer),
            "valor": sum(flt(p.valor_total) for p in a_vencer),
        },
        "recebido_mes": {
            "count": len(recebidas_mes),
            "valor": sum(flt(p.valor_total) for p in recebidas_mes),
        },
        "audiencias_semana": frappe.db.count(
            "Audiencia",
            {"data_hora": ["between", [f"{hoje} 00:00:00", f"{sete_dias} 23:59:59"]]},
        ),
        "prazos_urgentes": frappe.db.count(
            "Controle de Prazos",
            {
                "status": "Pendente",
                "data_prazo": ["<=", add_days(hoje, 3)],
            },
        ),
    }


def _build_alertas(hoje, sete_dias):
    alertas = []
    amanha = add_days(hoje, 1)

    prazos_criticos = frappe.get_all(
        "Controle de Prazos",
        filters={
            "status": "Pendente",
            "data_prazo": ["between", [hoje, amanha]],
        },
        fields=["name", "descricao", "data_prazo", "cliente", "servico", "prioridade"],
        order_by="data_prazo asc",
        limit_page_length=20,
    )
    for p in prazos_criticos:
        dias = date_diff(p.data_prazo, hoje)
        alertas.append(
            {
                "tipo": "prazo",
                "nivel": "red" if dias <= 0 else "yellow",
                "titulo": p.descricao or p.name,
                "data": p.data_prazo,
                "cliente": p.cliente or "",
                "dias": dias,
                "doctype": "Controle de Prazos",
                "docname": p.name,
            }
        )

    audiencias_hoje = frappe.get_all(
        "Audiencia",
        filters={"data_hora": ["between", [f"{hoje} 00:00:00", f"{hoje} 23:59:59"]]},
        fields=["name", "cliente", "data_hora", "tipo", "local_vara", "modalidade"],
        order_by="data_hora asc",
        limit_page_length=20,
    )
    for a in audiencias_hoje:
        alertas.append(
            {
                "tipo": "audiencia",
                "nivel": "yellow",
                "titulo": a.tipo or _("Audiência"),
                "data": str(a.data_hora)[:10] if a.data_hora else hoje,
                "hora": str(a.data_hora)[11:16] if a.data_hora else "",
                "cliente": a.cliente or "",
                "vara": _vara_label(a.local_vara),
                "modalidade": a.modalidade or "",
                "doctype": "Audiencia",
                "docname": a.name,
            }
        )

    return alertas


def _get_parcelas(hoje, limit_start, limit_page_length):
    rows = frappe.get_all(
        "Parcela de Honorarios",
        filters={"status": ["in", ["Vencida", "Pendente"]]},
        fields=PARCELA_FIELDS,
        order_by="vencimento asc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    return _enriquecer_parcelas(rows, hoje)


def _get_audiencias(hoje, sete_dias):
    rows = frappe.get_all(
        "Audiencia",
        filters={"data_hora": ["between", [f"{hoje} 00:00:00", f"{sete_dias} 23:59:59"]]},
        fields=[
            "name",
            "servico",
            "cliente",
            "data_hora",
            "tipo",
            "local_vara",
            "modalidade",
            "link_virtual",
        ],
        order_by="data_hora asc",
        limit_page_length=20,
    )
    for a in rows:
        data_hora = a.get("data_hora")
        if data_hora:
            a["data"] = str(data_hora)[:10]
            a["hora"] = str(data_hora)[11:16]
            a["dias_restantes"] = date_diff(a["data"], hoje)
        else:
            a["data"] = None
            a["hora"] = ""
            a["dias_restantes"] = 0
        a["vara_label"] = _vara_label(a.get("local_vara"))
        if a.get("servico") and not a.get("cliente"):
            a["cliente"] = frappe.db.get_value("Servico", a.servico, "cliente") or ""
    return rows


def _get_prazos(hoje, sete_dias):
    rows = frappe.get_all(
        "Controle de Prazos",
        filters={
            "status": "Pendente",
            "data_prazo": ["<=", sete_dias],
        },
        fields=["name", "descricao", "data_prazo", "prioridade", "servico", "cliente"],
        order_by="data_prazo asc",
        limit_page_length=20,
    )
    prioridade_ordem = {"Alta": 0, "Média": 1, "Media": 1, "Baixa": 2, "Normal": 3}
    for p in rows:
        p["dias_restantes"] = date_diff(p.data_prazo, hoje) if p.data_prazo else 0
        p["cliente_nome"] = p.cliente or ""
        if p.servico:
            sv = frappe.db.get_value(
                "Servico", p.servico, ["cliente", "title", "numero_processo"], as_dict=True
            )
            if sv:
                if not p["cliente_nome"]:
                    p["cliente_nome"] = sv.cliente or ""
                p["servico_titulo"] = sv.title or ""
                p["numero_processo"] = sv.numero_processo or ""
    rows.sort(
        key=lambda x: (
            prioridade_ordem.get(x.get("prioridade"), 9),
            x.get("dias_restantes", 99),
        )
    )
    return rows


def _get_tarefas(hoje, limit_start, limit_page_length):
    rows = frappe.get_all(
        "Tarefa",
        filters={"status": ["in", ["Pendente", "Em Andamento"]]},
        fields=["name", "titulo", "status", "prioridade", "data_limite", "servico", "responsavel"],
        order_by="data_limite asc, prioridade desc",
        limit_start=limit_start,
        limit_page_length=limit_page_length,
    )
    for t in rows:
        if t.data_limite:
            t["dias_restantes"] = date_diff(t.data_limite, hoje)
        else:
            t["dias_restantes"] = None
        t["cliente_nome"] = ""
        t["servico_titulo"] = ""
        if t.servico:
            sv = frappe.db.get_value(
                "Servico", t.servico, ["cliente", "title"], as_dict=True
            )
            if sv:
                t["cliente_nome"] = sv.cliente or ""
                t["servico_titulo"] = sv.title or ""
        if t.responsavel:
            t["responsavel_nome"] = frappe.db.get_value("User", t.responsavel, "full_name") or t.responsavel
        else:
            t["responsavel_nome"] = ""
    return rows


def _enriquecer_parcelas(parcelas, hoje):
    cache_acordo = {}
    for p in parcelas:
        if p.get("descrição") and not p.get("descricao"):
            p["descricao"] = p["descrição"]

        acordo_name = p.get("parent")
        if not acordo_name:
            continue

        if acordo_name not in cache_acordo:
            cache_acordo[acordo_name] = _load_acordo_context(acordo_name)

        info = cache_acordo[acordo_name]
        p["cliente_nome"] = info.get("cliente", "")
        p["servico_ref"] = info.get("servico", "")
        p["servico_titulo"] = info.get("servico_titulo", "")
        p["servico_tipo"] = info.get("servico_tipo", "")
        p["numero_processo"] = info.get("numero_processo", "")

        vencimento = p.get("vencimento")
        if vencimento:
            p["dias_atraso"] = max(date_diff(hoje, vencimento), 0)
            p["dias_para_vencer"] = max(date_diff(vencimento, hoje), 0)
        else:
            p["dias_atraso"] = 0
            p["dias_para_vencer"] = 0

    return parcelas


def _load_acordo_context(acordo_name):
    try:
        acordo = frappe.db.get_value(
            "Acordo de Honorarios Processuais",
            acordo_name,
            ["cliente", "servico", "modo_honorarios"],
            as_dict=True,
        )
        if not acordo:
            return {}

        ctx = {
            "cliente": acordo.cliente or "",
            "servico": acordo.servico or "",
            "modo": acordo.modo_honorarios or "",
            "servico_titulo": "",
            "servico_tipo": "",
            "numero_processo": "",
        }
        if acordo.servico:
            servico = frappe.db.get_value(
                "Servico",
                acordo.servico,
                ["title", "tipo", "numero_processo"],
                as_dict=True,
            )
            if servico:
                ctx["servico_titulo"] = servico.title or ""
                ctx["servico_tipo"] = servico.tipo or ""
                ctx["numero_processo"] = servico.numero_processo or ""
        return ctx
    except Exception:
        frappe.log_error(
            title="Painel: erro ao carregar acordo",
            message=frappe.get_traceback(),
        )
        return {}


def _vara_label(vara_link):
    if not vara_link:
        return ""
    try:
        return frappe.db.get_value("Vara", vara_link, "vara_name") or vara_link
    except Exception:
        return vara_link


@frappe.whitelist()
def marcar_parcela_recebida(parcela_name):
    """Marca uma Parcela de Honorarios como Recebida direto do Painel."""
    if not frappe.has_permission("Parcela de Honorarios", "write"):
        frappe.throw(_("Sem permissão"), frappe.PermissionError)

    doc = frappe.get_doc("Parcela de Honorarios", parcela_name)
    if doc.status in ("Recebida", "Repassada"):
        frappe.throw(_("Parcela já está {0}").format(doc.status))

    doc.status = "Recebida"
    doc.data_recebimento = today()
    doc.save(ignore_permissions=False)
    frappe.db.commit()

    return {"ok": True, "name": doc.name, "parent": doc.parent}
