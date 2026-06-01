import frappe
from frappe import _
from frappe.utils import add_days, cint, get_first_day, get_last_day, today

from advocacia.advocacia.painel import financeiro as painel_financeiro
from advocacia.advocacia.painel import kpis as painel_kpis
from advocacia.advocacia.painel import prazos as painel_prazos
from advocacia.advocacia.painel import timeline as painel_timeline
from advocacia.advocacia.painel._helpers import (
	LIST_LIMIT_MAX,
	_list_cap,
	_normalize_list_limits,
	_normalize_periodo_dias,
)


def get(
	limit_start=0,
	limit_page_length=20,
	periodo_dias=7,
	list_limit=5,
	list_limits=None,
):
	if not frappe.has_permission("Servico", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	limit_start = cint(limit_start)
	limit_page_length = min(cint(limit_page_length or 20), 100)
	periodo_dias = _normalize_periodo_dias(periodo_dias)
	list_limits = _normalize_list_limits(list_limits, list_limit)
	list_limit = list_limits["timeline"]

	hoje = today()
	periodo_fim = add_days(hoje, periodo_dias)
	amanha = add_days(hoje, 1)
	mes_inicio = get_first_day(hoje)
	mes_fim = get_last_day(hoje)

	kpis = painel_kpis._build_kpis(hoje, periodo_fim, mes_inicio, mes_fim)
	financeiro = painel_financeiro._build_financeiro(
		hoje, periodo_fim, mes_inicio, mes_fim, kpis, periodo_dias
	)
	resumo = painel_kpis._build_resumo(hoje, kpis, financeiro, periodo_dias)
	alertas = painel_prazos._build_alertas(hoje, periodo_fim)
	parcelas_cap = _list_cap(list_limits, "parcelas")
	despesas_cap = _list_cap(list_limits, "despesas")
	custas_cap = _list_cap(list_limits, "custas")
	comunicacoes_cap = _list_cap(list_limits, "comunicacoes")
	timeline_cap = _list_cap(list_limits, "timeline")
	tarefas_cap = timeline_cap

	parcelas_all = painel_financeiro._get_pagamentos_operacao(
		hoje, periodo_fim, limit_start, LIST_LIMIT_MAX
	)
	parcelas = parcelas_all[:parcelas_cap]
	audiencias = painel_prazos._get_audiencias(hoje, periodo_fim, LIST_LIMIT_MAX)
	prazos = painel_prazos._get_prazos(hoje, periodo_fim, LIST_LIMIT_MAX)
	tarefas_all = painel_timeline._get_tarefas(hoje, limit_start, LIST_LIMIT_MAX)
	tarefas = tarefas_all[:tarefas_cap]
	despesas_all = painel_financeiro._get_despesas_pendentes(LIST_LIMIT_MAX)
	despesas_pendentes = despesas_all[:despesas_cap]
	total_despesas_mes = painel_financeiro._get_total_despesas_mes(mes_inicio, mes_fim)
	custas_all = painel_financeiro._get_custas_pendentes_repasse(LIST_LIMIT_MAX)
	custas_pendentes_repasse = custas_all[:custas_cap]
	total_custas_mes = painel_financeiro._get_total_custas_mes(mes_inicio, mes_fim)
	comunicacoes_all = painel_timeline._get_comunicacoes_pendentes(LIST_LIMIT_MAX)
	comunicacoes_pendentes = comunicacoes_all[:comunicacoes_cap]
	ultimas_comunicacoes = comunicacoes_pendentes or painel_timeline._get_ultimas_comunicacoes(
		comunicacoes_cap
	)
	horas_semana = painel_timeline._get_horas_semana(hoje)
	horas_periodo = painel_timeline._get_horas_periodo(hoje, periodo_fim)
	centro_atencao = painel_prazos._build_centro_atencao(hoje, amanha, kpis, financeiro, tarefas)
	timeline_full = painel_timeline._build_timeline(
		hoje, periodo_fim, audiencias, prazos, tarefas_all
	)
	timeline = timeline_full[:timeline_cap]

	list_meta = {
		"timeline": {"showing": len(timeline), "total": len(timeline_full)},
		"comunicacoes": {"showing": len(comunicacoes_pendentes), "total": len(comunicacoes_all)},
		"parcelas": {"showing": len(parcelas), "total": len(parcelas_all)},
		"despesas": {"showing": len(despesas_pendentes), "total": len(despesas_all)},
		"custas": {"showing": len(custas_pendentes_repasse), "total": len(custas_all)},
	}

	return {
		"periodo_dias": periodo_dias,
		"list_limit": list_limit,
		"list_limits": list_limits,
		"list_meta": list_meta,
		"kpis": kpis,
		"resumo": resumo,
		"financeiro": financeiro,
		"alertas": alertas,
		"centro_atencao": centro_atencao,
		"timeline": timeline,
		"parcelas": parcelas,
		"despesas_pendentes": despesas_pendentes,
		"total_despesas_mes": total_despesas_mes,
		"custas_pendentes_repasse": custas_pendentes_repasse,
		"total_custas_mes": total_custas_mes,
		"comunicacoes_pendentes": comunicacoes_pendentes,
		"ultimas_comunicacoes": ultimas_comunicacoes,
		"horas_semana": horas_semana,
		"horas_periodo": horas_periodo,
		"audiencias": audiencias[:timeline_cap],
		"prazos": prazos[:timeline_cap],
		"tarefas": tarefas,
	}
