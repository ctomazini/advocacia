"""Generate manual_usuario.md from DocType JSONs."""

from __future__ import annotations

import json
import os
from pathlib import Path

DOCTYPE_ORDER = [
	("Cadastros Básicos", ["Client", "Jurisdiction", "Court Branch", "Court", "Case Phase"]),
	("Serviço Jurídico (Hub Central)", ["Legal Case"]),
	(
		"Financeiro",
		["Fee Agreement", "Legal Payment", "Court Cost", "Office Expense"],
	),
	(
		"Acompanhamento Processual",
		["Hearing", "Deadline", "Legal Task", "Case Communication"],
	),
	("Registro de Atividades", ["Service Record", "Time Entry"]),
	("Documentos", ["Document Template", "Document Kit"]),
	("Configuração", ["Office Settings"]),
]

DOCTYPE_DESCRIPTIONS = {
	"Client": (
		"Cadastro completo do cliente do escritório. Centraliza dados pessoais, "
		"documentação, endereços e contatos. Todo serviço jurídico está vinculado a um cliente."
	),
	"Legal Case": (
		"O **Serviço** é o DocType central (hub) do sistema. Representa um processo "
		"judicial ou consultoria jurídica. Audiências, prazos, pagamentos e atos orbitam um Serviço."
	),
	"Fee Agreement": (
		"Define honorários contratados com o cliente, parcelas e vencimentos. "
		"O sistema sincroniza parcelas com registros de Legal Payment."
	),
	"Legal Payment": (
		"Registro operacional de recebimento. Diferente da Parcela (contratual), "
		"registra o dinheiro que efetivamente entrou no escritório."
	),
	"Hearing": (
		"Audiências judiciais vinculadas a um serviço. Sincroniza com o calendário Frappe (Google Calendar)."
	),
	"Deadline": (
		"Prazos processuais com data fatal. Notificações automáticas usam "
		"`dias_notificacao` do prazo ou o padrão de Office Settings."
	),
	"Jurisdiction": "Divisão judiciária geográfica. Cadastro rígido para consistência.",
	"Court Branch": "Unidade judicial dentro de uma comarca.",
	"Court": "Court de justiça competente (ex.: TJRS, TRF4).",
	"Case Phase": "Fase do processo no fluxo (Distribuído, Sentenciado, etc.).",
	"Document Template": (
		"Modelo .docx com placeholders para geração automática. "
		"Use o botão **Ver Placeholders Disponíveis** para a lista completa."
	),
	"Document Kit": "Conjunto de templates para geração em lote.",
	"Office Settings": (
		"Dados institucionais do escritório: OAB, CNPJ, endereço, logo, dados bancários "
		"e dias padrão de antecedência para alertas de prazos."
	),
}

SKIP_TYPES = {"Section Break", "Column Break", "Tab Break", "HTML", "Fold"}


def _render_placeholders_section() -> list[str]:
	try:
		from advocacia.advocacia.documentos import PLACEHOLDER_REFERENCIA
	except ImportError:
		return []

	lines = [
		"### Placeholders para templates .docx",
		"",
		"Sintaxe **docxtpl**: `{{ nome_do_campo }}`. "
		"Grupos *condicionais* só têm valor quando há acordo de honorários vinculado. "
		"A logo usa `{{ escritorio_logo }}` como imagem inline.",
		"",
	]
	for block in PLACEHOLDER_REFERENCIA:
		if block.get("grupo", "").startswith("Legados"):
			continue
		tag = " *(condicional)*" if block.get("condicional") else ""
		lines.append(f"#### {block['grupo']}{tag}")
		lines.append("")
		lines.append("| Placeholder | Descrição | Alias legado |")
		lines.append("|-------------|-----------|--------------|")
		for item in block.get("items") or []:
			ph = f"`{{{{ {item['placeholder']} }}}}`"
			alias = f"`{{{{ {item['alias']} }}}}`" if item.get("alias") else "—"
			lines.append(f"| {ph} | {item.get('label', '')} | {alias} |")
		lines.append("")
	return lines


def _auto_describe(field: dict) -> str:
	ftype = field.get("fieldtype", "")
	options = field.get("options", "")
	fetch_from = field.get("fetch_from", "")
	if ftype == "Link" and options:
		return f"Selecione um registro de **{options}**."
	if ftype == "Select" and options:
		opts = [o for o in options.split("\n") if o.strip()]
		return f"Opções: {', '.join(opts)}"
	if ftype == "Currency":
		return "Valor em R$ (reais)."
	if ftype == "Date":
		return "Data no formato DD/MM/AAAA."
	if ftype == "Datetime":
		return "Data e hora."
	if ftype == "Check":
		return "Marque para ativar."
	if ftype == "Table" and options:
		return f"Tabela de itens (**{options}**)."
	if fetch_from:
		return f"Preenchido automaticamente a partir de `{fetch_from}`."
	return ""


def _load_field_descriptions() -> dict[str, dict[str, str]]:
	from advocacia.advocacia.scripts.add_field_descriptions import DESCRIPTIONS

	return DESCRIPTIONS


def generate():
	import frappe

	app_path = frappe.get_app_path("advocacia")
	doctype_path = os.path.join(app_path, "advocacia", "doctype")
	output_path = os.path.join(app_path, "docs", "manual_usuario.md")
	field_descs = _load_field_descriptions()
	os.makedirs(os.path.dirname(output_path), exist_ok=True)

	try:
		version = frappe.get_attr("advocacia.__version__")
	except Exception:
		version = "0.7.0"

	lines = [
		"# Manual do Usuário — Advocacia",
		"",
		f"**Gerado em:** {frappe.utils.today()}",
		f"**Versão do app:** {version}",
		"",
		"---",
		"",
		"## Visão Geral",
		"",
		"O sistema **Advocacia** centraliza clientes, processos, audiências, prazos, "
		"honorários, pagamentos e documentos para escritórios de advocacia brasileiros.",
		"",
		"O **Serviço** funciona como hub: audiências, prazos, pagamentos e atos orbitam um serviço.",
		"",
		"### Painel",
		"",
		"Acesse `/app/painel` para KPIs, listas rápidas (prazos, audiências, tarefas) e atalhos de criação.",
		"",
		"---",
		"",
	]
	field_count = 0

	for section_title, doctypes in DOCTYPE_ORDER:
		lines.append(f"## {section_title}")
		lines.append("")
		for dt_name in doctypes:
			slug = frappe.scrub(dt_name)
			json_path = os.path.join(doctype_path, slug, f"{slug}.json")
			lines.append(f"### {dt_name}")
			lines.append("")
			desc = DOCTYPE_DESCRIPTIONS.get(dt_name, "")
			if desc:
				lines.append(desc)
				lines.append("")
			if not os.path.exists(json_path):
				lines.append(f"*DocType não encontrado: {json_path}*")
				lines.append("")
				continue
			with open(json_path, encoding="utf-8") as f:
				dt_json = json.load(f)
			autoname = dt_json.get("autoname", "")
			if autoname:
				lines.append(f"**Código automático:** `{autoname}`")
				lines.append("")
			fields = [
				f
				for f in dt_json.get("fields", [])
				if f.get("fieldtype") not in SKIP_TYPES and not f.get("hidden")
			]
			if fields:
				lines.append("| Campo | Tipo | Obrigatório | Descrição |")
				lines.append("|-------|------|:-----------:|-----------|")
				dt_fields = field_descs.get(dt_name, {})
				for field in fields:
					fname = field.get("fieldname", "")
					label = field.get("label", fname)
					ftype = field.get("fieldtype", "")
					reqd = "✅" if field.get("reqd") else ""
					description = (
						dt_fields.get(fname) or field.get("description") or _auto_describe(field)
					)
					lines.append(f"| {label} | {ftype} | {reqd} | {description} |")
					field_count += 1
				lines.append("")
			lines.append("**Permissões:** Advocacia Manager (completo); Advocacia User conforme DocType.")
			lines.append("")
			lines.append("---")
			lines.append("")

		if section_title == "Documentos":
			lines.extend(_render_placeholders_section())

	lines.extend(
		[
			"## Fluxos Comuns",
			"",
			"### Novo Processo",
			"1. Cadastre o **Client**",
			"2. Crie um **Serviço** com vara, comarca e tribunal",
			"3. Defina **Acordo de Honorários** com parcelas",
			"4. Cadastre **Audiências** e **Prazos**",
			"",
			"### Recebimento",
			"1. Registre **Legal Payment** quando o cliente pagar",
			"2. O painel atualiza KPIs financeiros",
			"",
			"---",
			"",
			"*Regenerar: `bench execute advocacia.advocacia.scripts.generate_manual.generate`*",
		]
	)

	with open(output_path, "w", encoding="utf-8") as f:
		f.write("\n".join(lines))

	print(f"✅ Manual gerado: {output_path} ({field_count} campos)")


def main() -> None:
	generate()


if __name__ == "__main__":
	main()
