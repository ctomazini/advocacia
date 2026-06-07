#!/usr/bin/env python3
"""Split monolithic page/painel/painel.js into public/js/painel modules + painel.css."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "advocacia"
PAGE_JS = ROOT / "advocacia" / "page" / "painel" / "painel.js"
PAGE_CSS = ROOT / "advocacia" / "page" / "painel" / "painel.css"
OUT_DIR = ROOT / "public" / "js" / "painel"

MODULE_FUNCS = {
	"utils": [
		"cint",
		"flt",
		"painel_icon",
		"fmt_currency",
		"fmt_date_iso",
		"fmt_datetime",
		"_is_vencido",
		"_pagamento_pode_receber",
		"status_pill",
		"scroll_painel_section",
		"painel_default_list_limits",
		"painel_merge_list_limits",
		"render_list_limit_controls",
		"painel_periodo_fim",
		"painel_periodo_label",
		"painel_periodo_previsto_label",
		"painel_periodo_a_receber_label",
		"painel_periodo_recebidos_label",
		"painel_periodo_enunciado",
		"painel_periodo_scope_label",
		"painel_horas_label",
		"painel_list_meta_html",
		"painel_goto_list",
		"render_success_state",
		"render_empty_state",
		"painel_date_parts",
		"prazo_countdown_label",
		"painel_day_diff",
		"painel_timeline_when_label",
		"painel_polish_frappe_chrome",
	],
	"hero": [
		"painel_context_html",
		"painel_greeting",
		"render_header",
		"render_acoes_rapidas",
		"render_filtros_painel",
	],
	"kpis": [
		"render_centro_atencao",
		"painel_build_indicadores_items",
		"render_indicadores_painel",
		"painel_calc_saude_operacional",
		"render_saude_operacional",
		"render_kpis",
		"render_kpis_operacionais",
	],
	"audiencias": [
		"painel_find_proximas_audiencias",
		"painel_audiencia_modalidade_html",
		"painel_audiencia_entrar_html",
		"render_proxima_audiencia_card",
		"render_proxima_audiencia",
		"render_audiencia_items",
	],
	"timeline": [
		"render_timeline",
		"build_timeline_items",
		"render_comunicacoes_pendentes",
		"render_comunicacoes",
		"render_prazo_items",
		"render_tarefa_items",
		"render_operacao_dia",
	],
	"financeiro": [
		"painel_init_finance_chart",
		"render_financeiro",
		"build_parcelas_criticas",
		"render_duo_honorarios_despesas",
		"render_duo_custas_horas",
		"render_parcelas",
		"render_despesas",
		"render_custas",
		"render_horas_semana",
		"render_secundario",
	],
	"index": [
		"mostrar_skeleton",
		"handle_error",
		"load_painel",
		"render_painel",
		"bind_painel_filters",
		"bind_atencao_routes",
	],
}

FUNC_TO_MODULE = {}
for mod, names in MODULE_FUNCS.items():
	for name in names:
		FUNC_TO_MODULE[name] = mod

INDEX_RENAMES = {"load_painel": "load", "render_painel": "render"}


def extract_css(src: str) -> str:
	match = re.search(r"function inject_painel_styles\(\) \{.*?var css = `(.*?)`;", src, re.DOTALL)
	if not match:
		raise SystemExit("CSS block not found")
	lines = []
	for line in match.group(1).splitlines():
		lines.append(line[8:] if line.startswith("        ") else line)
	return "\n".join(lines) + "\n"


def parse_functions(lines: list[str]) -> dict[str, list[str]]:
	funcs: dict[str, list[str]] = {}
	i = 0
	while i < len(lines):
		m = re.match(r"^function (\w+)", lines[i])
		if m:
			name = m.group(1)
			body = [lines[i]]
			i += 1
			while i < len(lines) and not re.match(r"^function \w+", lines[i]):
				if lines[i].startswith("$(document).on("):
					break
				body.append(lines[i])
				i += 1
			funcs[name] = body
			continue
		i += 1
	return funcs


def extract_globals(lines: list[str]) -> str:
	start = next(i for i, line in enumerate(lines) if line.startswith("$(document).on("))
	return "\n".join(lines[start:])


def extract_var_block(lines: list[str]) -> list[str]:
	out: list[str] = []
	for i, line in enumerate(lines):
		if line.startswith("var PAINEL_LIST_LIMIT_KEYS"):
			j = i
			while j < len(lines) and not lines[j].startswith("function "):
				out.append(lines[j])
				j += 1
			break
	return out


def prefix_calls(code: str) -> str:
	replacements: list[tuple[str, str]] = []
	for name, mod in FUNC_TO_MODULE.items():
		if mod == "utils":
			replacements.append((name, f"U.{name}"))
		elif mod == "hero":
			replacements.append((name, f"H.{name}"))
		elif mod == "kpis":
			replacements.append((name, f"K.{name}"))
		elif mod == "audiencias":
			replacements.append((name, f"A.{name}"))
		elif mod == "timeline":
			replacements.append((name, f"T.{name}"))
		elif mod == "financeiro":
			replacements.append((name, f"F.{name}"))
		elif mod == "index":
			target = INDEX_RENAMES.get(name, name)
			replacements.append((name, f"AP.{target}"))

	# Longest names first to avoid partial replacements
	replacements.sort(key=lambda x: len(x[0]), reverse=True)
	for name, repl in replacements:
		code = re.sub(rf"\b{re.escape(name)}\b", repl, code)

	# Fix double-prefixed declarations
	code = re.sub(r"AP\.AP\.", "AP.", code)
	code = re.sub(r"U\.U\.", "U.", code)
	return code


def convert_function_lines(lines: list[str], export_name: str | None = None) -> list[str]:
	m = re.match(r"^function (\w+)(.*)", lines[0])
	if not m:
		return lines
	name = export_name or m.group(1)
	body_text = prefix_calls("\n".join(lines[1:]))
	body_lines = body_text.splitlines() if body_text else []
	out = [f"\tAP.{name} = function{m.group(2)}"]
	for line in body_lines:
		out.append("\t" + line if line else "")
	return out


def write_module(mod: str, func_names: list[str], funcs: dict[str, list[str]], extra_lines: list[str] | None = None):
	if mod == "utils":
		utils_parts = [
			"/* eslint-disable */",
			'frappe.provide("advocacia.painel.utils");',
			"(function (U) {",
		]
		if extra_lines:
			utils_parts.extend(extra_lines)
			utils_parts.append("")
		for fname in func_names:
			if fname not in funcs:
				continue
			m = re.match(r"^function (\w+)(.*)", funcs[fname][0])
			if not m:
				continue
			body_text = prefix_calls("\n".join(funcs[fname][1:]))
			utils_parts.append(f"\tU.{fname} = function{m.group(2)}")
			for line in body_text.splitlines():
				utils_parts.append("\t" + line if line else "")
			utils_parts.append("")
		code = "\n".join(utils_parts) + "\n})(advocacia.painel.utils = advocacia.painel.utils || {});\n"
		(OUT_DIR / f"{mod}.js").write_text(code, encoding="utf-8")
		return

	parts: list[str] = [
		"/* eslint-disable */",
		f'frappe.provide("advocacia.painel.{mod}");',
		"(function (AP) {",
		"\tvar U = advocacia.painel.utils;",
		"\tvar H = advocacia.painel.hero;",
		"\tvar K = advocacia.painel.kpis;",
		"\tvar A = advocacia.painel.audiencias;",
		"\tvar T = advocacia.painel.timeline;",
		"\tvar F = advocacia.painel.financeiro;",
		"",
	]

	if mod == "index":
		parts = [
			"/* eslint-disable */",
			'frappe.provide("advocacia.painel");',
			"",
			"advocacia.painel.init = function (wrapper) {",
			"\tvar page = frappe.ui.make_app_page({",
			"\t\tparent: wrapper,",
			'\t\ttitle: __("Painel do Escritório"),',
			"\t\tsingle_column: true,",
			"\t});",
			"",
			'\tpage.painel_container = $(\'<div class="painel-root"></div>\').appendTo(page.main);',
			"\tadvocacia.painel.utils.painel_polish_frappe_chrome();",
			"",
			'\tpage.add_button(__("↺ Atualizar"), function () {',
			"\t\tadvocacia.painel.load(page);",
			"\t});",
			"",
			"\tfrappe.pages.painel.page = page;",
			"\tpage.painel_periodo = 7;",
			"\tpage.painel_list_limits = advocacia.painel.utils.painel_default_list_limits();",
			"\tadvocacia.painel.load(page);",
			"};",
			"",
			"(function (AP) {",
			"\tvar U = advocacia.painel.utils;",
			"\tvar H = advocacia.painel.hero;",
			"\tvar K = advocacia.painel.kpis;",
			"\tvar A = advocacia.painel.audiencias;",
			"\tvar T = advocacia.painel.timeline;",
			"\tvar F = advocacia.painel.financeiro;",
			"",
		]

	body_lines: list[str] = []
	for fname in func_names:
		if fname not in funcs:
			continue
		export = INDEX_RENAMES.get(fname, fname) if mod == "index" else fname
		body_lines.extend(convert_function_lines(funcs[fname], export))
		body_lines.append("")

	code = "\n".join(parts + body_lines)
	if mod == "index":
		code += "\n})(advocacia.painel);\n"
	else:
		code += f"\n}})(advocacia.painel.{mod} = advocacia.painel.{mod} || {{}});\n"
	(OUT_DIR / f"{mod}.js").write_text(code, encoding="utf-8")


def write_loader():
	loader = '''frappe.pages.painel = frappe.pages.painel || {};

frappe.pages.painel.on_page_load = function (wrapper) {
\tif (typeof advocacia !== "undefined" && advocacia.painel && advocacia.painel.init) {
\t\tadvocacia.painel.init(wrapper);
\t} else {
\t\tfrappe.msgprint(__("Módulos do painel não carregados. Execute bench build --app advocacia."));
\t}
};

frappe.pages.painel.on_page_hide = function () {
\t$(document.body).removeClass("advocacia-painel-active");
};
'''
	PAGE_JS.write_text(loader, encoding="utf-8")


def main():
	# Always read monolith backup if present (page loader may have been replaced)
	monolith = ROOT / "advocacia" / "page" / "painel" / "painel.monolith.js"
	if not monolith.exists():
		raise SystemExit("Missing painel.monolith.js backup — restore from git first")
	src = monolith.read_text(encoding="utf-8")
	PAGE_CSS.write_text(extract_css(src), encoding="utf-8")
	lines = src.splitlines()
	funcs = parse_functions(lines)
	var_block = ["\t" + line for line in extract_var_block(lines)]

	OUT_DIR.mkdir(parents=True, exist_ok=True)
	write_module("utils", MODULE_FUNCS["utils"], funcs, extra_lines=var_block)

	for mod in ("hero", "kpis", "audiencias", "timeline", "financeiro"):
		write_module(mod, MODULE_FUNCS[mod], funcs)

	write_module("index", MODULE_FUNCS["index"], funcs)
	index_path = OUT_DIR / "index.js"
	index_text = index_path.read_text(encoding="utf-8").rstrip()
	globals_code = extract_globals(lines)
	globals_code = prefix_calls(globals_code)
	globals_code = globals_code.replace("AP.load", "advocacia.painel.load")
	globals_code = globals_code.replace(
		"if (page && typeof AP.load === \"function\") AP.load(page);",
		"if (page && advocacia.painel.load) { advocacia.painel.load(page); }",
	)
	globals_code = globals_code.replace("U.painel_goto_list", "advocacia.painel.utils.painel_goto_list")
	globals_code = globals_code.replace("U.scroll_painel_section", "advocacia.painel.utils.scroll_painel_section")
	index_text += "\n\n" + globals_code + "\n"
	index_path.write_text(index_text, encoding="utf-8")

	write_loader()
	print(f"Split complete → {OUT_DIR}")


if __name__ == "__main__":
	main()
