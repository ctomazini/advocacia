"""Generate manual_usuario.md from DocType JSONs."""

from __future__ import annotations

import json
import os
from pathlib import Path

DOCTYPE_ORDER = [
	("Cadastros Básicos", ["Cliente", "Comarca", "Vara", "Tribunal", "Fase Processual"]),
	("Serviço Jurídico (Hub Central)", ["Servico"]),
	(
		"Financeiro",
		["Acordo de Honorarios Processuais", "Pagamento", "Custa Processual", "Despesa do Escritorio"],
	),
	(
		"Acompanhamento Processual",
		["Audiencia", "Controle de Prazos", "Tarefa", "Comunicacao"],
	),
	("Registro de Atividades", ["Registro de Atos", "Registro de Horas"]),
	("Documentos", ["Template Documento", "Kit de Documentos"]),
	("Configuração", ["Configuracao do Escritorio"]),
]

DOCTYPE_DESCRIPTIONS = {
	"Cliente": (
		"Cadastro completo do cliente do escritório. Centraliza dados pessoais, "
		"documentação, endereços e contatos. Todo serviço jurídico está vinculado a um cliente."
	),
	"Servico": (
		"O **Serviço** é o DocType central (hub) do sistema. Representa um processo "
		"judicial ou consultoria jurídica. Audiências, prazos, pagamentos e atos orbitam um Serviço."
	),
	"Acordo de Honorarios Processuais": (
		"Define honorários contratados com o cliente, parcelas e vencimentos. "
		"O sistema sincroniza parcelas com registros de Pagamento."
	),
	"Pagamento": (
		"Registro operacional de recebimento. Diferente da Parcela (contratual), "
		"registra o dinheiro que efetivamente entrou no escritório."
	),
	"Audiencia": (
		"Audiências judiciais vinculadas a um serviço. Sincroniza com o calendário Frappe (Google Calendar)."
	),
	"Controle de Prazos": (
		"Prazos processuais com data fatal. Notificações automáticas para prazos urgentes (≤3 dias)."
	),
	"Comarca": "Divisão judiciária geográfica. Cadastro rígido para consistência.",
	"Vara": "Unidade judicial dentro de uma comarca.",
	"Tribunal": "Tribunal de justiça competente (ex.: TJRS, TRF4).",
	"Fase Processual": "Fase do processo no fluxo (Distribuído, Sentenciado, etc.).",
	"Template Documento": "Modelo .docx com placeholders para geração automática.",
	"Kit de Documentos": "Conjunto de templates para geração em lote.",
	"Configuracao do Escritorio": "Dados institucionais do escritório (OAB, CNPJ, endereço).",
}

SKIP_TYPES = {"Section Break", "Column Break", "Tab Break", "HTML", "Fold", "Button"}


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

	lines.extend(
		[
			"## Fluxos Comuns",
			"",
			"### Novo Processo",
			"1. Cadastre o **Cliente**",
			"2. Crie um **Serviço** com vara, comarca e tribunal",
			"3. Defina **Acordo de Honorários** com parcelas",
			"4. Cadastre **Audiências** e **Prazos**",
			"",
			"### Recebimento",
			"1. Registre **Pagamento** quando o cliente pagar",
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
	root = Path(__file__).resolve().parents[1] / "doctype"
	out = Path(__file__).resolve().parents[1] / "docs" / "manual_usuario.md"
	field_descs = {}
	try:
		from advocacia.advocacia.scripts.add_field_descriptions import DESCRIPTIONS

		field_descs = DESCRIPTIONS
	except ImportError:
		pass

	# minimal offline stub — prefer bench execute
	print(f"Use bench execute para gerar. DocTypes em {root}")


if __name__ == "__main__":
	main()
