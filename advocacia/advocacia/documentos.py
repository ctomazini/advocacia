import io
import json
import os
import re
import uuid
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import cint, flt, formatdate, fmt_money, getdate, today

from advocacia.advocacia.validators import (
	formatar_cep,
	formatar_cnj,
	formatar_cnpj,
	formatar_cpf,
	formatar_telefone,
)
from num2words import num2words as _num2words

TEMPLATE_CATEGORY_MAP = {
	"procuracao": "Procuração",
	"procuração": "Procuração",
	"mandato": "Procuração",
	"contrato": "Contrato",
	"honorario": "Contrato",
	"honorários": "Contrato",
	"acordo": "Acordo",
	"peticao": "Petição",
	"petição": "Petição",
	"inicial": "Petição",
	"contestacao": "Petição",
	"contestação": "Petição",
	"recurso": "Petição",
	"substabelecimento": "Substabelecimento",
	"declaracao": "Outro",
	"declaração": "Outro",
	"certidao": "Certidão",
	"certidão": "Certidão",
	"decisao": "Decisão",
	"decisão": "Decisão",
	"sentenca": "Decisão",
	"sentença": "Decisão",
	"comprovante": "Comprovante",
	"recibo": "Comprovante",
	"protocolo": "Protocolo",
	"requerimento": "Protocolo",
	"laudo": "Laudo",
}

DOCUMENT_TYPE_CATEGORY_MAP = {
	"Contrato": "Contrato",
	"Declaracao": "Outro",
	"Recibo": "Comprovante",
	"Carta": "Outro",
	"Ficha de Atendimento": "Outro",
	"Outro": "Outro",
}

LEGACY_PLACEHOLDERS = [
	"nome",
	"cpf",
	"cnpj",
	"rg",
	"nacionalidade",
	"estado_civil",
	"profissao",
	"telefone",
	"email",
	"representante",
	"cpf_representante",
	"endereco",
	"numero",
	"complemento",
	"bairro",
	"cidade",
	"estado",
	"cep",
	"legal_case",
	"tipo_servico",
	"titulo_servico",
	"numero_processo",
	"area",
	"court_branch_link",
	"jurisdiction",
	"parte_contraria",
	"valor_causa",
	"data_abertura",
	"telefone_contato",
]

PLACEHOLDER_REFERENCIA = [
	{
		"grupo": "Escritório",
		"items": [
			{"placeholder": "escritorio_razao_social", "label": "Razão social do escritório"},
			{"placeholder": "escritorio_cnpj", "label": "CNPJ do escritório (mascarado)"},
			{"placeholder": "escritorio_oab", "label": "OAB do escritório"},
			{"placeholder": "escritorio_advogada", "label": "Advogada(o) principal"},
			{"placeholder": "escritorio_advogada_cpf", "label": "CPF da advogada principal (mascarado)"},
			{"placeholder": "escritorio_advogada_rg", "label": "RG da advogada principal"},
			{"placeholder": "escritorio_endereco", "label": "Endereço profissional"},
			{"placeholder": "escritorio_registro", "label": "Registro SIA/OAB"},
			{
				"placeholder": "escritorio_logo",
				"label": "Logo do escritório (imagem — somente em .docx)",
			},
			{"placeholder": "escritorio_banco", "label": "Banco"},
			{"placeholder": "escritorio_agencia", "label": "Agência"},
			{"placeholder": "escritorio_conta", "label": "Conta corrente"},
			{"placeholder": "escritorio_pix", "label": "Chave PIX"},
		],
	},
	{
		"grupo": "Cliente",
		"items": [
			{"placeholder": "cliente_nome", "label": "Nome / razão social", "alias": "nome"},
			{"placeholder": "cliente_tipo_pessoa", "label": "Tipo de pessoa (PF/PJ)"},
			{"placeholder": "cliente_cpf", "label": "CPF (mascarado)", "alias": "cpf"},
			{"placeholder": "cliente_cnpj", "label": "CNPJ (mascarado)", "alias": "cnpj"},
			{"placeholder": "cliente_rg", "label": "RG", "alias": "rg"},
			{"placeholder": "cliente_data_nascimento", "label": "Data de nascimento (dd/MM/yyyy)"},
			{"placeholder": "cliente_rg_emissor", "label": "Órgão emissor do RG"},
			{"placeholder": "cliente_nacionalidade", "label": "Nacionalidade", "alias": "nacionalidade"},
			{"placeholder": "cliente_estado_civil", "label": "Estado civil", "alias": "estado_civil"},
			{"placeholder": "cliente_profissao", "label": "Profissão", "alias": "profissao"},
			{"placeholder": "cliente_representante", "label": "Representante legal", "alias": "representante"},
			{
				"placeholder": "cliente_cpf_representante",
				"label": "CPF do representante",
				"alias": "cpf_representante",
			},
			{"placeholder": "cliente_cargo_representante", "label": "Cargo do representante"},
			{"placeholder": "cliente_nome_fantasia", "label": "Nome fantasia"},
		],
	},
	{
		"grupo": "Endereço do cliente",
		"items": [
			{"placeholder": "endereco_logradouro", "label": "Logradouro", "alias": "endereco"},
			{"placeholder": "endereco_numero", "label": "Número", "alias": "numero"},
			{"placeholder": "endereco_complemento", "label": "Complemento", "alias": "complemento"},
			{"placeholder": "endereco_bairro", "label": "Bairro", "alias": "bairro"},
			{"placeholder": "endereco_cidade", "label": "Cidade", "alias": "cidade"},
			{"placeholder": "endereco_estado", "label": "UF", "alias": "estado"},
			{"placeholder": "endereco_cep", "label": "CEP (mascarado)", "alias": "cep"},
			{"placeholder": "endereco_completo", "label": "Endereço completo formatado"},
		],
	},
	{
		"grupo": "Contato",
		"items": [
			{"placeholder": "contato_nome", "label": "Nome do contato"},
			{"placeholder": "contato_telefone", "label": "Telefone fixo", "alias": "telefone"},
			{"placeholder": "contato_celular", "label": "Celular"},
			{"placeholder": "contato_email", "label": "E-mail", "alias": "email"},
			{"placeholder": "telefone_contato", "label": "Telefone principal (legado)"},
		],
	},
	{
		"grupo": "Processo",
		"items": [
			{"placeholder": "servico_codigo", "label": "Código do serviço (ID)", "alias": "legal_case"},
			{"placeholder": "servico_titulo", "label": "Título do serviço", "alias": "titulo_servico"},
			{"placeholder": "servico_tipo", "label": "Tipo de serviço", "alias": "tipo_servico"},
			{"placeholder": "servico_status", "label": "Status do serviço"},
			{
				"placeholder": "servico_numero_processo",
				"label": "Número do processo (CNJ)",
				"alias": "numero_processo",
			},
			{"placeholder": "servico_area", "label": "Área jurídica", "alias": "area"},
			{"placeholder": "servico_vara", "label": "Vara", "alias": "court_branch_link"},
			{"placeholder": "servico_comarca", "label": "Comarca", "alias": "jurisdiction"},
			{"placeholder": "servico_tribunal", "label": "Tribunal"},
			{"placeholder": "servico_fase_processual", "label": "Fase processual"},
			{
				"placeholder": "servico_parte_contraria",
				"label": "Parte contrária",
				"alias": "parte_contraria",
			},
			{
				"placeholder": "servico_valor_causa",
				"label": "Valor da causa (R$)",
				"alias": "valor_causa",
			},
			{
				"placeholder": "servico_data_abertura",
				"label": "Data de abertura",
				"alias": "data_abertura",
			},
		],
	},
	{
		"grupo": "Cobranças de Honorários (condicional)",
		"condicional": True,
		"items": [
			{"placeholder": "acordo_modo_honorarios", "label": "Modo de honorários"},
			{"placeholder": "acordo_status", "label": "Status dos honorários"},
			{"placeholder": "acordo_valor_total_do_acordo", "label": "Valor total contratado (R$)"},
			{"placeholder": "acordo_percentual_advogada", "label": "Percentual da advogada (%)"},
			{"placeholder": "acordo_valor_fixo_de_honorarios", "label": "Valor fixo de honorários (R$)"},
			{"placeholder": "acordo_valor_advogada", "label": "Valor da advogada (R$)"},
			{"placeholder": "acordo_numero_de_parcelas", "label": "Número de parcelas"},
			{"placeholder": "acordo_data_primeira_parcela", "label": "Data da 1ª parcela"},
			{"placeholder": "acordo_valor_da_parcela", "label": "Valor da parcela (R$)"},
			{"placeholder": "acordo_total_advogada", "label": "Total advogada (R$)"},
			{"placeholder": "acordo_total_cliente", "label": "Total cliente (R$)"},
			{"placeholder": "acordo_valor_extenso", "label": "Valor total contratado por extenso"},
			{
				"placeholder": "acordo_narrativa_pagamento",
				"label": "Narrativa agrupada das parcelas (parágrafos separados por linha em branco)",
			},
			{
				"placeholder": "acordo_parcelas",
				"label": "Lista de parcelas (use {% for p in acordo_parcelas %})",
			},
		],
	},
	{
		"grupo": "Parcela do acordo (loop)",
		"condicional": True,
		"condicional_motivo": "Campos dentro de {% for p in acordo_parcelas %}",
		"items": [
			{"placeholder": "payment_condition", "label": "Condição de pagamento", "loop_only": True, "loop_var": "p"},
			{"placeholder": "due_date", "label": "Vencimento", "loop_only": True, "loop_var": "p"},
			{"placeholder": "due_date_fmt", "label": "Vencimento formatado", "loop_only": True, "loop_var": "p"},
			{"placeholder": "lawyer_amount", "label": "Valor advogada (R$)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "lawyer_amount_fmt", "label": "Valor advogada formatado", "loop_only": True, "loop_var": "p"},
			{"placeholder": "total_amount", "label": "Valor total da parcela (R$)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "total_amount_fmt", "label": "Valor total formatado", "loop_only": True, "loop_var": "p"},
			{"placeholder": "client_amount", "label": "Valor cliente (R$)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "contingency_amount", "label": "Valor sucumbência (R$)", "loop_only": True, "loop_var": "p"},
			{"placeholder": "status", "label": "Status", "loop_only": True, "loop_var": "p"},
			{"placeholder": "description", "label": "Descrição", "loop_only": True, "loop_var": "p"},
			{"placeholder": "received_date", "label": "Data de recebimento", "loop_only": True, "loop_var": "p"},
			{"placeholder": "received_date_fmt", "label": "Data de recebimento formatada", "loop_only": True, "loop_var": "p"},
		],
	},
	{
		"grupo": "Data",
		"items": [
			{"placeholder": "data_hoje", "label": "Data de hoje (dd/MM/yyyy)"},
			{"placeholder": "data_hoje_extenso", "label": "Data de hoje por extenso"},
		],
	},
	{
		"grupo": "Legados (compatibilidade)",
		"items": [{"placeholder": p, "label": p} for p in LEGACY_PLACEHOLDERS],
	},
]


def get_document_placeholder_keys() -> set[str]:
	"""Chaves documentadas na referência (inclui aliases legados)."""
	keys = set()
	for block in PLACEHOLDER_REFERENCIA:
		for item in block.get("items") or []:
			if item.get("loop_only"):
				continue
			keys.add(item["placeholder"])
			if item.get("alias"):
				keys.add(item["alias"])
	return keys


def _formatar_moeda(valor):
	if valor in (None, ""):
		return ""
	return fmt_money(flt(valor), currency="BRL")


def _formatar_data(valor):
	if not valor:
		return ""
	return formatdate(getdate(valor), "dd/MM/yyyy")


def _formatar_percentual(valor):
	if valor in (None, ""):
		return ""
	return f"{flt(valor):g}%"


def _formatar_data_extenso(data_str):
	meses = [
		"",
		"janeiro",
		"fevereiro",
		"março",
		"abril",
		"maio",
		"junho",
		"julho",
		"agosto",
		"setembro",
		"outubro",
		"novembro",
		"dezembro",
	]
	if isinstance(data_str, str):
		dt = datetime.strptime(data_str, "%Y-%m-%d")
	else:
		dt = data_str
	return f"{dt.day} de {meses[dt.month]} de {dt.year}"


def _valor_por_extenso(value) -> str:
	amount = flt(value)
	if not amount:
		return ""
	try:
		return _num2words(amount, lang="pt_BR", to="currency")
	except Exception:
		return ""


def _contagem_por_extenso(n: int) -> str:
	if n == 1:
		return "uma"
	if n == 2:
		return "duas"
	return _num2words(n, lang="pt_BR")


def _parcela_valor_principal(parcela) -> float:
	valor = flt(getattr(parcela, "lawyer_amount", None))
	if not valor:
		valor = flt(getattr(parcela, "total_amount", None))
	return valor


def _linha_parcela_narrativa(parcela) -> dict:
	return {
		"payment_condition": getattr(parcela, "payment_condition", None) or "Data fixa",
		"due_date": getattr(parcela, "due_date", None) or "",
		"amount": _parcela_valor_principal(parcela),
		"status": getattr(parcela, "status", None) or "",
		"description": getattr(parcela, "description", None) or "",
	}


def _montar_narrativa_pagamento(installments: list[dict]) -> str:
	if not installments:
		return ""

	active = [row for row in installments if row.get("status") != "Cancelado"]
	if not active:
		return ""

	fixed = [
		row
		for row in active
		if (row.get("payment_condition") or "Data fixa") == "Data fixa" and row.get("due_date")
	]
	non_fixed = [row for row in active if row not in fixed]
	parts = []

	if fixed:
		groups = []
		current_group = [fixed[0]]
		for i in range(1, len(fixed)):
			prev_amount = flt(current_group[0]["amount"])
			curr_amount = flt(fixed[i]["amount"])
			amounts_match = abs(curr_amount - prev_amount) <= 0.02
			if amounts_match:
				current_group.append(fixed[i])
			else:
				is_last = i == len(fixed) - 1
				diff_pct = abs(curr_amount - prev_amount) / prev_amount * 100 if prev_amount else 100
				if is_last and diff_pct <= 5 and len(current_group) >= 2:
					current_group.append(fixed[i])
				else:
					groups.append(current_group)
					current_group = [fixed[i]]
		groups.append(current_group)

		for group in groups:
			count = len(group)
			main_amount = flt(group[0]["amount"])
			start_date = group[0]["due_date"]
			try:
				day = getdate(start_date).day
			except Exception:
				day = None
			last_amount = flt(group[-1]["amount"])
			has_adjustment = count > 1 and abs(last_amount - main_amount) > 0.02
			count_display = f"{count:02d}" if count < 100 else str(count)
			count_words = _contagem_por_extenso(count)
			amount_fmt = _formatar_moeda(main_amount)
			amount_words = _valor_por_extenso(main_amount)
			start_date_fmt = _formatar_data(start_date)
			if count == 1:
				line = f"{count_display} ({count_words}) parcela de {amount_fmt} ({amount_words})"
				if day:
					line += f", com vencimento em {start_date_fmt}"
			else:
				line = f"{count_display} ({count_words}) parcelas de {amount_fmt} ({amount_words})"
				line += " mensais e consecutivas"
				if day:
					line += f" com pagamento todo dia {day:02d}"
				line += f", a iniciar em {start_date_fmt}"
			if has_adjustment:
				adj_fmt = _formatar_moeda(last_amount)
				adj_words = _valor_por_extenso(last_amount)
				line += f", sendo a última parcela no valor de {adj_fmt} ({adj_words})"
			line += "."
			parts.append(line)

	condition_text = {
		"Na conclusão": "a ser paga na conclusão do serviço",
		"Na sentença": "a ser paga na prolação da sentença",
		"A definir": "com data a definir",
	}
	for row in non_fixed:
		amount = flt(row["amount"])
		amount_fmt = _formatar_moeda(amount)
		amount_words = _valor_por_extenso(amount)
		condition = row.get("payment_condition") or "A definir"
		suffix = condition_text.get(condition, "com data a definir")
		desc = row.get("description")
		if desc:
			line = f"01 (uma) parcela de {amount_fmt} ({amount_words}) referente a {desc.lower()}, {suffix}."
		else:
			line = f"01 (uma) parcela de {amount_fmt} ({amount_words}), {suffix}."
		parts.append(line)

	return "\n\n".join(parts)


def _linha_parcela_acordo(parcela) -> dict:
	lawyer_amount = _parcela_valor_principal(parcela)
	total_amount = flt(getattr(parcela, "total_amount", None))
	client_amount = flt(getattr(parcela, "client_amount", None))
	contingency_amount = flt(getattr(parcela, "contingency_amount", None))
	received_date = getattr(parcela, "received_date", None)
	return {
		"payment_condition": getattr(parcela, "payment_condition", None) or "Data fixa",
		"due_date": getattr(parcela, "due_date", None) or "",
		"due_date_fmt": _formatar_data(getattr(parcela, "due_date", None)),
		"lawyer_amount": lawyer_amount,
		"lawyer_amount_fmt": _formatar_moeda(lawyer_amount),
		"total_amount": total_amount,
		"total_amount_fmt": _formatar_moeda(total_amount),
		"client_amount": client_amount,
		"contingency_amount": contingency_amount,
		"status": getattr(parcela, "status", None) or "",
		"description": getattr(parcela, "description", None) or "",
		"received_date": received_date or "",
		"received_date_fmt": _formatar_data(received_date),
	}


def _parcela_due_date_sort_key(due_date) -> tuple:
	"""Ordena parcelas por vencimento; vazias por último; normaliza str/date."""
	if not due_date:
		return (1, getdate("9999-12-31"))
	return (0, getdate(due_date))


def _contexto_acordo(acordo) -> dict:
	empty = {
		"acordo_valor_extenso": "",
		"acordo_narrativa_pagamento": "",
		"acordo_parcelas": [],
	}
	if not acordo:
		return empty

	parcelas = sorted(
		acordo.fee_installments or [],
		key=lambda row: _parcela_due_date_sort_key(row.due_date),
	)
	linhas = [_linha_parcela_acordo(row) for row in parcelas]
	narrativa_rows = [_linha_parcela_narrativa(row) for row in parcelas]
	return {
		"acordo_valor_extenso": _valor_por_extenso(acordo.total_agreement_value),
		"acordo_narrativa_pagamento": _montar_narrativa_pagamento(narrativa_rows),
		"acordo_parcelas": linhas,
	}


def _link_label(doctype, name):
	if not name:
		return ""
	if not frappe.db.exists(doctype, name):
		return name
	return frappe.db.get_value(doctype, name, "name") or name


def _get_endereco_principal(cliente):
	if not cliente.addresses:
		return None
	principal = next((row for row in cliente.addresses if row.is_primary), None)
	return principal or cliente.addresses[0]


def _get_contato_principal(cliente):
	if not cliente.contacts:
		return None
	principal = next(
		(row for row in cliente.contacts if (row.type or "").lower() == "principal"),
		None,
	)
	return principal or cliente.contacts[0]


def _get_acordo(servico_name):
	acordo_name = frappe.db.get_value(
		"Fee Agreement",
		{"legal_case": servico_name, "docstatus": ["!=", 2]},
		"name",
	)
	if not acordo_name:
		return None
	return frappe.get_doc("Fee Agreement", acordo_name)


def _montar_endereco_completo(addr):
	if not addr:
		return ""
	partes = []
	logradouro = addr.get("street") or ""
	numero = addr.get("number") or ""
	if logradouro:
		partes.append(f"{logradouro}{', ' + numero if numero else ''}")
	complemento = addr.get("complement") or ""
	if complemento:
		partes.append(complemento)
	bairro = addr.get("neighborhood") or ""
	if bairro:
		partes.append(f"Bairro {bairro}")
	cidade = addr.get("city") or ""
	estado = addr.get("state") or ""
	if cidade or estado:
		partes.append("/".join(filter(None, [cidade, estado])))
	cep = formatar_cep(addr.get("cep"))
	if cep:
		partes.append(f"CEP {cep}")
	return " — ".join(partes)


def _get_escritorio_context():
	"""Lê dados do escritório do Single DocType (somente banco, nunca hardcoded)."""
	cfg = frappe.get_single("Office Settings")
	cnpj_raw = cfg.cnpj or ""
	cnpj_fmt = formatar_cnpj(cnpj_raw) if cnpj_raw else ""
	cpf_raw = cfg.lawyer_cpf or ""
	cpf_fmt = formatar_cpf(cpf_raw) if cpf_raw else ""
	return {
		"escritorio_razao_social": cfg.company_name or "",
		"escritorio_cnpj": cnpj_fmt,
		"escritorio_oab": cfg.oab or "",
		"escritorio_advogada": cfg.lawyer_name or "",
		"escritorio_advogada_cpf": cpf_fmt,
		"escritorio_advogada_rg": cfg.lawyer_rg or "",
		"escritorio_endereco": cfg.address or "",
		"escritorio_registro": cfg.sia_registration or "",
		"escritorio_banco": cfg.bank_name or "",
		"escritorio_agencia": cfg.bank_agency or "",
		"escritorio_conta": cfg.bank_account or "",
		"escritorio_pix": cfg.bank_pix or "",
		"escritorio_logo": "",
	}


def _inject_logo_context(tpl, context):
	"""Insere InlineImage no contexto quando há logo configurada."""
	logo_url = frappe.db.get_single_value("Office Settings", "office_logo")
	if not logo_url:
		context["escritorio_logo"] = ""
		return

	try:
		from docx.shared import Mm
		from docxtpl import InlineImage
	except ImportError:
		context["escritorio_logo"] = ""
		return

	file_name = frappe.db.get_value("File", {"file_url": logo_url}, "name")
	if not file_name:
		context["escritorio_logo"] = ""
		return

	logo_path = frappe.get_doc("File", file_name).get_full_path()
	if not os.path.exists(logo_path):
		context["escritorio_logo"] = ""
		return

	context["escritorio_logo"] = InlineImage(tpl, logo_path, width=Mm(25))


def _build_context(servico_name):
	if not frappe.has_permission("Legal Case", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	servico = frappe.get_doc("Legal Case", servico_name)
	cliente = frappe.get_doc("Client", servico.client)
	addr = _get_endereco_principal(cliente)
	contato = _get_contato_principal(cliente)
	acordo = _get_acordo(servico.name)
	hoje = today()

	tipo_pessoa = cliente.person_type or ""
	cpf_raw = cliente.cpf or ""
	cnpj_raw = cliente.cnpj or ""
	cpf_fmt = formatar_cpf(cpf_raw) if tipo_pessoa == "Pessoa Física" else ""
	cnpj_fmt = formatar_cnpj(cnpj_raw) if tipo_pessoa == "Pessoa Jurídica" else ""

	celular = contato.get("mobile") if contato else ""
	telefone_fixo = contato.get("phone") if contato else ""
	telefone = celular or telefone_fixo or ""
	email = (contato.get("email") if contato else "") or ""

	context = _get_escritorio_context()
	context.update(
		{
			"cliente_nome": cliente.client_name or "",
			"cliente_tipo_pessoa": tipo_pessoa,
			"cliente_cpf": cpf_fmt,
			"cliente_cnpj": cnpj_fmt,
			"cliente_rg": cliente.rg or "",
			"cliente_data_nascimento": _formatar_data(cliente.birth_date),
			"cliente_rg_emissor": cliente.rg_issuer or "",
			"cliente_nacionalidade": cliente.nationality or "",
			"cliente_estado_civil": cliente.marital_status or "",
			"cliente_profissao": cliente.occupation or "",
			"cliente_representante": cliente.representative or "",
			"cliente_cpf_representante": formatar_cpf(cliente.representative_cpf),
			"cliente_cargo_representante": cliente.representative_role or "",
			"cliente_nome_fantasia": cliente.trade_name or "",
			"endereco_logradouro": addr.street if addr else "",
			"endereco_numero": addr.number if addr else "",
			"endereco_complemento": addr.complement if addr else "",
			"endereco_bairro": addr.neighborhood if addr else "",
			"endereco_cidade": addr.city if addr else "",
			"endereco_estado": addr.state if addr else "",
			"endereco_cep": formatar_cep(addr.cep if addr else ""),
			"endereco_completo": _montar_endereco_completo(addr.as_dict() if addr else None),
			"contato_telefone": formatar_telefone(telefone),
			"contato_celular": formatar_telefone(celular),
			"contato_email": (email or "").lower(),
			"contato_nome": contato.get("contact_name") if contato else "",
			"telefone_contato": formatar_telefone(telefone),
			"servico_titulo": servico.title or "",
			"servico_tipo": servico.type or "",
			"servico_status": servico.status or "",
			"servico_numero_processo": formatar_cnj(servico.case_number),
			"servico_area": servico.area or "",
			"servico_vara": _link_label("Court Branch", servico.court_branch_link),
			"servico_comarca": _link_label("Jurisdiction", servico.jurisdiction),
			"servico_tribunal": _link_label("Court", servico.court),
			"servico_fase_processual": _link_label("Case Phase", servico.case_phase),
			"servico_parte_contraria": servico.opposing_party or "",
			"servico_valor_causa": _formatar_moeda(servico.case_value),
			"servico_data_abertura": _formatar_data(servico.opening_date),
			"data_hoje": formatdate(getdate(hoje), "dd/MM/yyyy"),
			"data_hoje_extenso": _formatar_data_extenso(hoje),
		}
	)

	acordo_defaults = {
		"acordo_modo_honorarios": "",
		"acordo_status": "",
		"acordo_valor_total_do_acordo": "",
		"acordo_percentual_advogada": "",
		"acordo_valor_fixo_de_honorarios": "",
		"acordo_valor_advogada": "",
		"acordo_numero_de_parcelas": "",
		"acordo_data_primeira_parcela": "",
		"acordo_valor_da_parcela": "",
		"acordo_total_advogada": "",
		"acordo_total_cliente": "",
		"acordo_valor_extenso": "",
		"acordo_narrativa_pagamento": "",
		"acordo_parcelas": [],
	}
	context.update(acordo_defaults)

	if acordo:
		context.update(
			{
				"acordo_modo_honorarios": acordo.fee_mode or "",
				"acordo_status": acordo.status or "",
				"acordo_valor_total_do_acordo": _formatar_moeda(acordo.total_agreement_value),
				"acordo_percentual_advogada": _formatar_percentual(acordo.lawyer_percentage),
				"acordo_valor_fixo_de_honorarios": _formatar_moeda(acordo.fixed_fee_amount),
				"acordo_valor_advogada": _formatar_moeda(acordo.lawyer_amount),
				"acordo_numero_de_parcelas": cint(acordo.get("installment_count") or 0) or "",
				"acordo_data_primeira_parcela": _formatar_data(acordo.first_installment_date),
				"acordo_valor_da_parcela": _formatar_moeda(acordo.installment_amount),
				"acordo_total_advogada": _formatar_moeda(acordo.lawyer_total),
				"acordo_total_cliente": _formatar_moeda(acordo.client_total),
			}
		)
		context.update(_contexto_acordo(acordo))

	context.update(
		{
			"servico_codigo": servico.name,
			"legal_case": servico.name,
			"tipo_servico": context["servico_tipo"],
			"titulo_servico": context["servico_titulo"],
			"numero_processo": context["servico_numero_processo"],
			"area": context["servico_area"],
			"court_branch_link": context["servico_vara"],
			"jurisdiction": context["servico_comarca"],
			"parte_contraria": context["servico_parte_contraria"],
			"valor_causa": context["servico_valor_causa"],
			"data_abertura": context["servico_data_abertura"],
			"nome": context["cliente_nome"],
			"cpf": context["cliente_cpf"],
			"cnpj": context["cliente_cnpj"],
			"rg": context["cliente_rg"],
			"nacionalidade": context["cliente_nacionalidade"],
			"estado_civil": context["cliente_estado_civil"],
			"profissao": context["cliente_profissao"],
			"telefone": context["contato_telefone"],
			"email": context["contato_email"],
			"representante": context["cliente_representante"],
			"cpf_representante": context["cliente_cpf_representante"],
			"endereco": context["endereco_logradouro"],
			"numero": context["endereco_numero"],
			"complemento": context["endereco_complemento"],
			"bairro": context["endereco_bairro"],
			"cidade": context["endereco_cidade"],
			"estado": context["endereco_estado"],
			"cep": context["endereco_cep"],
		}
	)

	return context


def _render_document(servico_name, template_doc, context):
	try:
		from docxtpl import DocxTemplate
	except ImportError:
		frappe.throw(_("Biblioteca docxtpl nao instalada. Contate o administrador."))

	if not template_doc.template_file:
		frappe.throw(_("Template sem arquivo .docx anexado."))

	file_doc = frappe.get_doc("File", {"file_url": template_doc.template_file})
	file_path = file_doc.get_full_path()
	if not os.path.exists(file_path):
		frappe.throw(_("Arquivo do template nao encontrado no servidor."))

	tpl = DocxTemplate(file_path)
	_inject_logo_context(tpl, context)
	tpl.render(context)

	buffer = io.BytesIO()
	tpl.save(buffer)
	buffer.seek(0)

	timestamp = frappe.utils.now_datetime().strftime("%Y%m%d_%H%M%S")
	nome_arquivo = "{0}_{1}_{2}.docx".format(
		re.sub(r"[^\w\-]+", "_", template_doc.title).strip("_"),
		servico_name,
		timestamp,
	)

	return {"file_name": nome_arquivo, "content": buffer.read()}


def _infer_category(template_doc) -> str:
	search_text = " ".join(
		part
		for part in (
			template_doc.title,
			template_doc.document_type,
			template_doc.description,
		)
		if part
	).lower()
	for keyword, category in TEMPLATE_CATEGORY_MAP.items():
		if keyword in search_text:
			return category
	doc_type = (template_doc.document_type or "").strip()
	return DOCUMENT_TYPE_CATEGORY_MAP.get(doc_type, "Outro")


def _ensure_document_category(category_name: str) -> str:
	if not frappe.db.exists("Document Category", category_name):
		frappe.get_doc(
			{"doctype": "Document Category", "category_name": category_name}
		).insert(ignore_permissions=True)  # registro filho — categoria inferida do template
	return category_name


def _create_generated_case_document(
	servico_name: str,
	template_doc,
	file_url: str,
) -> str:
	category = _ensure_document_category(_infer_category(template_doc))
	doc = frappe.get_doc(
		{
			"doctype": "Case Document",
			"legal_case": servico_name,
			"category": category,
			"status": "Rascunho",
			"source": "Gerado pelo App",
			"file": file_url,
			"version_label": "v1",
		}
	)
	doc.insert(ignore_permissions=True)  # registro filho — write no serviço já validada
	return doc.name


_DOWNLOAD_CACHE_TTL = 300


def _stash_generated_download(file_name: str, content: bytes) -> str:
	key = f"adv_gen_doc:{uuid.uuid4().hex}"
	frappe.cache.set_value(
		key,
		{
			"user": frappe.session.user,
			"file_name": file_name,
			"content": content,
		},
		expires_in_sec=_DOWNLOAD_CACHE_TTL,
	)
	return key


def _get_cached_download(key: str) -> dict:
	"""Lê o download do cache sem consumir — mantém válido até o TTL.

	Não destrutivo para que o link visível de fallback continue funcionando
	mesmo após o download automático (browsers que bloqueiam auto-download).
	"""
	if not key or not key.startswith("adv_gen_doc:"):
		frappe.throw(_("Chave de download inválida."))

	payload = frappe.cache.get_value(key)
	if not payload:
		frappe.throw(_("Download expirado. Gere o documento novamente."))

	if payload.get("user") != frappe.session.user:
		frappe.throw(_("Sem permissão para este download."), frappe.PermissionError)

	return payload


@frappe.whitelist(methods=["GET"])
def download_generated_document(key: str) -> None:
	"""Entrega .docx gerado com Content-Disposition — download direto na pasta padrão."""
	frappe.has_permission("Legal Case", "read", throw=True)
	payload = _get_cached_download(key)
	frappe.local.response.filename = payload["file_name"]
	frappe.local.response.filecontent = payload["content"]
	frappe.local.response.type = "download"


def _parse_template_names(template_names):
	if isinstance(template_names, str):
		template_names = json.loads(template_names or "[]")
	if not isinstance(template_names, list):
		frappe.throw(_("Lista de templates inválida."))
	return [name for name in template_names if name]


@frappe.whitelist()
def gerar_documentos_em_lote(servico_name: str, template_names: str | list) -> dict:
	frappe.has_permission("Legal Case", "read", throw=True)

	nomes = _parse_template_names(template_names)
	if not nomes:
		frappe.throw(_("Selecione ao menos um template."))

	context = _build_context(servico_name)
	gerados = []
	falhas = []

	for template_name in nomes:
		try:
			template_doc = frappe.get_doc("Document Template", template_name)
			if not template_doc.enabled:
				raise frappe.ValidationError(_("Template desabilitado: {0}").format(template_name))
			result = _render_document(servico_name, template_doc, context)
			gerados.append(
				{
					"template": template_name,
					"title": template_doc.title,
					"file_name": result["file_name"],
					"download_key": _stash_generated_download(
						result["file_name"], result["content"]
					),
				}
			)
		except Exception as exc:
			falhas.append({"template": template_name, "erro": str(exc)})
			frappe.log_error(
				title=f"Erro ao gerar documento {template_name}",
				message=frappe.get_traceback(),
			)

	return {
		"success": True,
		"data": {
			"gerados": gerados,
			"falhas": falhas,
			"total": len(gerados),
		},
	}


@frappe.whitelist()
def get_templates_disponiveis() -> list[dict]:
	frappe.has_permission("Document Template", "read", throw=True)
	return frappe.get_all(
		"Document Template",
		fields=["name", "title", "document_type", "description"],
		filters={"enabled": 1},
		order_by="title",
		limit_page_length=500,
	)


@frappe.whitelist()
def get_kits_disponiveis() -> list[dict]:
	frappe.has_permission("Document Kit", "read", throw=True)

	kits = frappe.get_all(
		"Document Kit",
		fields=["name", "title", "description"],
		filters={"enabled": 1},
		order_by="title",
		limit_page_length=500,
	)
	if not kits:
		return kits

	kit_names = [kit.name for kit in kits]
	item_rows = frappe.get_all(
		"Document Kit Item",
		filters={"parent": ["in", kit_names]},
		fields=["parent", "template", "display_order"],
		order_by="parent asc, display_order asc, idx asc",
		limit_page_length=0,  # kits pequenos — carrega todos os itens
	)
	templates_por_kit = {name: [] for name in kit_names}
	for row in item_rows:
		if row.template:
			templates_por_kit.setdefault(row.parent, []).append(row.template)

	for kit in kits:
		kit["templates"] = templates_por_kit.get(kit.name, [])
	return kits


@frappe.whitelist()
def get_placeholders_referencia() -> dict:
	"""Referência organizada de placeholders para UI e templates."""
	frappe.has_permission("Document Template", "read", throw=True)
	return PLACEHOLDER_REFERENCIA
