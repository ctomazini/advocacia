#!/usr/bin/env python3
"""Regenerate CODEBASE.md from live DocType JSON and repo metrics."""

import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DT_DIR = ROOT / "advocacia/advocacia/doctype"
OUT_PATH = ROOT / "CODEBASE.md"


def esc(s):
	if s is None:
		return ""
	return str(s).replace("|", "/").replace("\n", " ")


def md_table(headers, rows):
	lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
	for r in rows:
		lines.append("| " + " | ".join(esc(c) for c in r) + " |")
	return "\n".join(lines) + "\n\n"


def count_lines(ext):
	total = 0
	for p in ROOT.rglob(f"*{ext}"):
		if ".git" in p.parts or "__pycache__" in p.parts:
			continue
		try:
			with open(p, encoding="utf-8", errors="ignore") as f:
				total += sum(1 for _ in f)
		except OSError:
			pass
	return total


def render_dt(name, d):
	meta_line = (
		f"**Meta:** autoname=`{d.get('autoname')}` · naming_rule=`{d.get('naming_rule', '')}` · "
		f"title_field=`{d.get('title_field', '')}` · istable={d.get('istable', 0)} · "
		f"issingle={d.get('issingle', 0)}"
	)
	rows = []
	for f in sorted(d.get("fields", []), key=lambda x: x.get("idx") or 0):
		ft = f.get("fieldtype", "")
		if ft in ("Section Break", "Column Break", "Tab Break"):
			continue
		opts = (f.get("options") or "").replace("\n", " ")
		if len(opts) > 60:
			opts = opts[:57] + "..."
		rows.append([
			f.get("fieldname", ""),
			f.get("label", ""),
			ft,
			opts,
			"✓" if f.get("reqd") else "",
			"✓" if f.get("unique") else "",
		])
	return (
		f"### {name}\n\n{meta_line}\n\n"
		+ md_table(["fieldname", "label", "fieldtype", "options", "reqd", "unique"], rows)
	)


def load_doctypes():
	child_tables, standalone, auxiliary, single = [], [], [], []
	for folder in sorted(DT_DIR.iterdir()):
		jpath = folder / f"{folder.name}.json"
		if not jpath.exists():
			continue
		d = json.loads(jpath.read_text(encoding="utf-8"))
		name = d.get("name") or folder.name
		if d.get("istable"):
			child_tables.append((name, d))
		elif d.get("issingle"):
			single.append((name, d))
		elif name in ("Jurisdiction", "Court Branch", "Court", "Case Phase"):
			auxiliary.append((name, d))
		else:
			standalone.append((name, d))
	return child_tables, standalone, auxiliary, single


def main():
	py_lines = count_lines(".py")
	js_lines = count_lines(".js")
	test_dir = ROOT / "advocacia/advocacia/tests"
	test_files = sorted(test_dir.glob("test_*.py"))
	test_methods = sum(
		len(re.findall(r"^\s+def test_", tf.read_text(encoding="utf-8", errors="ignore"), re.M))
		for tf in test_files
	)
	head = subprocess.check_output(
		["git", "log", "-1", "--format=%h %ci %s"], cwd=ROOT, text=True
	).strip()
	recent = subprocess.check_output(["git", "log", "--oneline", "-12"], cwd=ROOT, text=True).strip()
	child_tables, standalone, auxiliary, single = load_doctypes()

	L = []
	L.append("# CODEBASE — App Advocacia (Frappe v16)\n\n")
	L.append(
		f"> Gerado em **{date.today().isoformat()}** — re-audit pós-UX (títulos, list views, sidebar, painel). "
		"Branch **`frappe-v16`**. Frappe puro, **sem ERPNext**.\n\n"
	)
	L.append(f"> **HEAD:** `{head}`\n\n---\n\n")

	L.append("## 1. Visão Geral\n\n")
	L.append(
		md_table(
			["Item", "Valor"],
			[
				["Nome", "advocacia"],
				["Versão", "0.6.0 (`pyproject.toml`)"],
				["Framework", "Frappe v16.19.0"],
				["Licença", "MIT"],
				["Branch", "frappe-v16"],
				["Remote", "git@github.com:ctomazini/advocacia.git"],
				["Site dev", "advocacia.local (porta 8000)"],
				["Linhas Python", f"~{py_lines}"],
				["Linhas JavaScript", f"~{js_lines}"],
				["Métodos de teste", str(test_methods)],
				["DocTypes", "24 (todos `custom: 0`)"],
				["Script Reports", "6"],
			],
		)
	)
	L.append(
		"**Propósito:** LegalTech BR — clientes, serviços/processos, honorários, pagamentos, atos, "
		"prazos, audiências, despesas, registro de horas, painel, documentos `.docx`.\n\n"
		"**Deps:** `docxtpl>=0.18.0`; jquery.inputmask (Frappe).\n\n"
	)
	L.append("### 1.1 Entregas recentes (jun/2026)\n\n")
	L.append("| Área | Mudança |\n| --- | --- |\n")
	for a, b in [
		("Naming", "`format:PREFIX-{YYYY}-{####}` + `naming_rule: Expression`"),
		("Títulos", "`titulos.py`: `{ID} — {descritor}`; `show_title_field_in_link`"),
		("List views", "12 `*_list.js` com `hide_name_column` e `states`"),
		("Client", "`title_field=nome`; badge ID em `cliente_list.js`"),
		("Legal Payment", "Coluna Origem (`tipo_origem` + link Acordo/Registro)"),
		("Painel", "Nomes legíveis via `painel/`; `painel.js` ~4100 linhas"),
		("Sidebar", "`collapsible: 1` nas seções (fix scroll Frappe v16)"),
	]:
		L.append(f"| **{a}** | {b} |\n")
	L.append(f"\n**Commits recentes:**\n```text\n{recent}\n```\n\n")

	L.append("## 2. Árvore de Arquivos (anotada)\n\n```text\n")
	L.append("advocacia/\n├── CODEBASE.md, README.md, pyproject.toml\n└── advocacia/\n")
	L.append("    ├── hooks.py, modules.txt, patches.txt, patches/v16_0/\n")
	L.append("    ├── fixtures/, workspace_sidebar/advocacia.json\n")
	L.append("    ├── public/js/ (4: masks, list_nav, cliente_from_servico, timer_global)\n")
	L.append("    └── advocacia/\n")
	L.append("        ├── validators.py, titulos.py, painel_api.py (facade)\n")
	L.append("        ├── painel/ (kpis, financeiro, prazos, timeline, _helpers)\n")
	L.append("        ├── documentos.py, financeiro.py, tasks.py, notificacoes.py, calendar_sync.py\n")
	L.append("        ├── setup/ (install, sidebar, workspace, reports, translations, seed_demo)\n")
	L.append("        ├── tests/ (33 arquivos), doctype/ (24), page/painel/, report/ (6), workspace/\n")
	L.append("```\n\n")

	L.append("## 3. Mapa de DocTypes (24)\n\n")
	L.append(
		"Colunas: `fieldname` | label | fieldtype | options | reqd | unique. "
		"Section/Column/Tab breaks omitidos.\n\n"
	)
	for section, group in [
		("Standalone / transacionais", standalone),
		("Auxiliares (cadastro rígido)", auxiliary),
		("Child tables", child_tables),
		("Single", single),
	]:
		L.append(f"#### {section}\n\n")
		for name, d in sorted(group, key=lambda x: x[0]):
			L.append(render_dt(name, d))
	L.append(
		"### Grafo de links (resumo)\n\n"
		"`Client` ← Legal Case, Legal Payment, Acordo, … · `Jurisdiction` ← Court Branch, Legal Case · "
		"`Legal Case` hub → Prazos, Hearing, Atos, Horas, Custas · "
		"`Acordo` → `Fee Installment` → Legal Payment · "
		"`Service Record` → `Legal Act Item` (`cobranca_id` Link Legal Payment) · "
		"Auxiliares: Jurisdiction, Court Branch, Court, Case Phase.\n\n"
	)

	L.append("## 4. hooks.py\n\n### fixtures\n")
	L.append("Workspace Advocacia; Notifications prazo/audiência; Custom Field Event `custom_source%`.\n\n")
	L.append("### app_include_js (4)\n")
	for js in ("masks.js", "list_nav.js", "cliente_from_servico.js", "timer_global.js"):
		L.append(f"- `/assets/advocacia/js/{js}`\n")
	L.append(
		"\n**Removidos:** `navegacao.js`, widget painel global, `servico_link.js` "
		"(label de Serviço em `legal_case_query` / `format_servico_link_label`).\n\n"
	)
	L.append("### doc_events\n\n")
	L.append(
		md_table(
			["DocType", "Evento", "Handler"],
			[
				["Fee Agreement", "on_update", "financeiro.sincronizar_pagamentos_hook"],
				["Fee Installment", "on_update", "tasks.on_parcela_update"],
				["Legal Payment", "on_update", "financeiro.processar_pagamento_on_update"],
				["Legal Payment", "on_trash", "financeiro.on_pagamento_trash"],
				["Hearing", "after_insert / on_update", "calendar_sync.sync_audiencia_to_event"],
				["Deadline", "after_insert / on_update", "calendar_sync.sync_prazo_to_event"],
			],
		)
	)
	L.append("### scheduler_events\n")
	L.append(
		"- **daily:** verificar_parcelas_vencidas, verificar_despesas_vencidas, "
		"notificar_parcelas_vencidas, notificar_audiencias_hoje, notificar_prazos_diario\n"
		"- **weekly:** verificar_status_servicos\n\n"
	)
	L.append("### after_migrate\n")
	L.append(
		"reinstalar_istable → after_install → event fields → translations → sidebar → reports → workspace\n\n"
	)

	L.append("## 5. API whitelisted\n\n")
	L.append(
		md_table(
			["Função", "Módulo", "Permissão", "Chamador"],
			[
				["get_painel_data", "painel_api → painel.get", "Legal Case read", "painel.js xcall"],
				["marcar_parcela_recebida", "painel_api → painel.financeiro", "Legal Payment write", "painel.js"],
				["legal_case_query", "legal_case", "query", "Link Legal Case"],
				["gerar_documento_servico / em_lote", "documentos", "Legal Case read/write", "servico.js"],
				["get_kits_disponiveis", "documentos", "read", "servico.js"],
				["get_placeholders_referencia", "documentos", "Template read", "template_documento.js"],
				["registrar_recebimento/repasse", "parcela", "write", "form"],
				["concluir", "legal_task", "write", "tarefa.js"],
				["timer APIs", "registro_de_horas", "write", "timer_global.js"],
				["get_events", "audiencia/prazos", "calendar read", "*_calendar.js"],
				["gerar_proxima_despesa", "despesa", "create", "form"],
				["financeiro sync", "financeiro", "has_permission", "hooks"],
			],
		)
	)
	L.append("\n**xcall:** `advocacia.advocacia.painel_api.get_painel_data` (facade — não alterar no JS).\n\n")

	L.append("## 6. Schedulers\n\nVer §4 (`tasks.py`, `notificacoes.py`). Sem `commit()` em request/scheduler.\n\n")
	L.append("## 7. Client JS\n\n")
	L.append("- Globais (4), 12 list formatters, forms (acordo, servico, audiencia Híbrida).\n")
	L.append("- `painel.js` ~4100 linhas; CSS vars para charts.\n")
	L.append("- Calendários: `audiencia_calendar.js`, `controle_de_prazos_calendar.js`.\n\n")
	L.append("## 8. Setup / migrations\n\n")
	L.append("Idempotente; `commit()` só em setup/patches/seed (`seed_demo.py` = dev only).\n\n")
	L.append("## 9. Reports (6)\n\n")
	for r in (
		"carteira_ativa",
		"fluxo_de_caixa",
		"honorarios_por_cliente",
		"inadimplencia",
		"horas_por_servico",
		"produtividade",
	):
		L.append(f"- {r}\n")
	L.append("\nStatus Legal Payment: Pendente, Vencido, Recebido, Cancelado, Renegociado, Repassado.\n\n")
	L.append("## 10. Fixtures / Workspace / Sidebar\n\n")
	L.append("- 26 links sidebar ↔ workspace.\n")
	L.append("- Seções com `collapsible: 1` (Frappe v16).\n\n")
	L.append("## 11. Testes\n\n")
	L.append(f"- **{test_methods}** métodos em **{len(test_files)}** arquivos.\n")
	L.append("- `bench --site advocacia.local run-tests --app advocacia`\n")
	L.append("- Última run (site dev): **221** testes, **OK** (jun/2026).\n\n")
	L.append("## 12. Integrações\n\n")
	L.append("- calendar_sync → Event; documentos → docxtpl; Office Settings (Single).\n\n")
	L.append("## 13. Backlog consciente\n\n")
	L.append("1. Chart.js → frappe.ui.Chart\n")
	L.append("2. Fieldnames EN auxiliares (`city`, `case_phase_name`)\n")
	L.append("3. sql → qb no painel\n")
	L.append("4. Modularizar `painel.js`\n\n")

	L.append("## 14. Re-audit e prontidão para produção\n\n")
	L.append("### 14.1 Checklist (13 categorias)\n\n")
	L.append(
		md_table(
			["#", "Categoria", "Status", "Notas"],
			[
				["1", "Naming / autoname", "✅", "{YYYY} + Expression nos transacionais"],
				["2", "Link vs Data", "✅", "Auxiliares + pagamento em atos (fieldname cobranca_id)"],
				["3", "Validators", "✅", "validators.py + controllers"],
				["4", "db.commit", "✅", "Só setup/patches/seed/backfill"],
				["5", "ignore_permissions", "⚠️", "comunicacao, calendar_sync; seed_demo dev"],
				["6", "Whitelisted", "✅", "permission checks nos endpoints críticos"],
				["7", "N+1 / limits", "✅", "painel refatorado"],
				["8", "Dead code", "✅", "P0–P4b limpeza"],
				["9", "JS = UX", "✅", "Negócio em Python"],
				["10", "Hooks", "✅", "Legal Payment handler único; schedulers"],
				["11", "Workspace/sidebar", "✅", "collapsible fix"],
				["12", "Testes", "✅", "221/221 OK"],
				["13", "Reinstall limpo", "⏳", "Obrigatório pré go-live"],
			],
		)
	)
	L.append("### 14.2 Ajustes de teste (2026-06-02)\n\n")
	L.append(
		"- `test_titulos`: expectativa `{ID} — {descritor}` quando o usuário define título manual.\n"
		"- `test_criar_pj_valido`: CNPJ único via `_gerar_cnpj_valido()`.\n"
		"- `test_sem_prazos_urgentes_nao_envia`: mock de `get_all` isolado de dados demo.\n\n"
	)
	L.append("### 14.3 Veredito\n\n")
	L.append(
		"| Critério | OK? |\n| --- | --- |\n"
		"| Código Git (custom:0) | ✅ |\n"
		"| Blocos auditoria 1–4 | ✅ |\n"
		"| UX jun/2026 | ✅ (smoke manual) |\n"
		"| Suite 221/221 verde | ✅ |\n"
		"| install-app site limpo | ⏳ recomendado pré go-live |\n\n"
		"**Conclusão:** código e testes **prontos para produção**; validar reinstall limpo e smoke manual do painel/sidebar antes do go-live.\n"
	)

	text = "".join(L)
	OUT_PATH.write_text(text, encoding="utf-8")
	count = text.count("\n### ")
	print(f"Wrote {OUT_PATH} ({len(text.splitlines())} lines, {count} DocType headers)")
	assert count >= 24, f"expected 24+ ### headers, got {count}"


if __name__ == "__main__":
	main()
