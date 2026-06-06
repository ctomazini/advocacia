import io
import json
import os
import re
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import cint, flt, formatdate, fmt_money, getdate, today

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
	"servico",
	"tipo_servico",
	"titulo_servico",
	"numero_processo",
	"area",
	"vara",
	"comarca",
	"parte_contraria",
	"valor_causa",
	"data_abertura",
	"telefone_contato",
]

PLACEHOLDER_REFERENCIA = [
	{
		"grupo": "Escritório",
		"items": [
			{"placeholder": "escritorio_razao_social", "label": "Razão Social"},
			{"placeholder": "escritorio_cnpj", "label": "CNPJ"},
			{"placeholder": "escritorio_oab", "label": "OAB"},
			{"placeholder": "escritorio_advogada", "label": "Advogada"},
			{"placeholder": "escritorio_endereco", "label": "Endereço"},
			{"placeholder": "escritorio_registro", "label": "Registro SIA"},
		],
	},
	{
		"grupo": "Cliente",
		"items": [
			{"placeholder": "cliente_nome", "label": "Nome / Razão Social", "alias": "nome"},
			{"placeholder": "cliente_tipo_pessoa", "label": "Tipo de Pessoa"},
			{"placeholder": "cliente_cpf", "label": "CPF (mascarado)", "alias": "cpf"},
			{"placeholder": "cliente_cnpj", "label": "CNPJ (mascarado)", "alias": "cnpj"},
			{"placeholder": "cliente_rg", "label": "RG", "alias": "rg"},
			{"placeholder": "cliente_nacionalidade", "label": "Nacionalidade", "alias": "nacionalidade"},
			{"placeholder": "cliente_estado_civil", "label": "Estado Civil", "alias": "estado_civil"},
			{"placeholder": "cliente_profissao", "label": "Profissão", "alias": "profissao"},
			{"placeholder": "cliente_representante", "label": "Representante Legal", "alias": "representante"},
			{
				"placeholder": "cliente_cpf_representante",
				"label": "CPF do Representante",
				"alias": "cpf_representante",
			},
			{"placeholder": "cliente_cargo_representante", "label": "Cargo do Representante"},
			{"placeholder": "cliente_nome_fantasia", "label": "Nome Fantasia"},
		],
	},
	{
		"grupo": "Endereço",
		"items": [
			{"placeholder": "endereco_logradouro", "label": "Logradouro", "alias": "endereco"},
			{"placeholder": "endereco_numero", "label": "Número", "alias": "numero"},
			{"placeholder": "endereco_complemento", "label": "Complemento", "alias": "complemento"},
			{"placeholder": "endereco_bairro", "label": "Bairro", "alias": "bairro"},
			{"placeholder": "endereco_cidade", "label": "Cidade", "alias": "cidade"},
			{"placeholder": "endereco_estado", "label": "Estado", "alias": "estado"},
			{"placeholder": "endereco_cep", "label": "CEP (mascarado)", "alias": "cep"},
			{"placeholder": "endereco_completo", "label": "Endereço completo formatado"},
		],
	},
	{
		"grupo": "Contato",
		"items": [
			{"placeholder": "contato_telefone", "label": "Telefone", "alias": "telefone"},
			{"placeholder": "contato_celular", "label": "Celular"},
			{"placeholder": "contato_email", "label": "E-mail", "alias": "email"},
			{"placeholder": "contato_nome", "label": "Nome do contato"},
			{"placeholder": "telefone_contato", "label": "Telefone (legado)", "alias": "telefone_contato"},
		],
	},
	{
		"grupo": "Serviço",
		"items": [
			{"placeholder": "servico_titulo", "label": "Título", "alias": "titulo_servico"},
			{"placeholder": "servico_tipo", "label": "Tipo", "alias": "tipo_servico"},
			{"placeholder": "servico_status", "label": "Status"},
			{
				"placeholder": "servico_numero_processo",
				"label": "Número do processo (CNJ)",
				"alias": "numero_processo",
			},
			{"placeholder": "servico_area", "label": "Área", "alias": "area"},
			{"placeholder": "servico_vara", "label": "Vara", "alias": "vara"},
			{"placeholder": "servico_comarca", "label": "Comarca", "alias": "comarca"},
			{"placeholder": "servico_tribunal", "label": "Tribunal"},
			{"placeholder": "servico_fase_processual", "label": "Fase Processual"},
			{
				"placeholder": "servico_parte_contraria",
				"label": "Parte Contrária",
				"alias": "parte_contraria",
			},
			{
				"placeholder": "servico_valor_causa",
				"label": "Valor da Causa",
				"alias": "valor_causa",
			},
			{
				"placeholder": "servico_data_abertura",
				"label": "Data de Abertura",
				"alias": "data_abertura",
			},
		],
	},
	{
		"grupo": "Acordo",
		"condicional": True,
		"items": [
			{"placeholder": "acordo_modo_honorarios", "label": "Modo de Honorários"},
			{"placeholder": "acordo_status", "label": "Status"},
			{"placeholder": "acordo_valor_total_do_acordo", "label": "Valor Total do Acordo"},
			{"placeholder": "acordo_percentual_advogada", "label": "Percentual Advogada"},
			{"placeholder": "acordo_valor_fixo_de_honorarios", "label": "Valor Fixo de Honorários"},
			{"placeholder": "acordo_valor_advogada", "label": "Valor Advogada"},
			{"placeholder": "acordo_numero_de_parcelas", "label": "Número de Parcelas"},
			{"placeholder": "acordo_data_primeira_parcela", "label": "Data Primeira Parcela"},
			{"placeholder": "acordo_valor_da_parcela", "label": "Valor da Parcela"},
			{"placeholder": "acordo_total_advogada", "label": "Total Advogada"},
			{"placeholder": "acordo_total_cliente", "label": "Total Cliente"},
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


def _only_digits(value):
	if not value:
		return ""
	return re.sub(r"\D", "", str(value))


def _mascarar_cpf(valor):
	digits = _only_digits(valor)
	if len(digits) != 11:
		return valor or ""
	return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"


def _mascarar_cnpj(valor):
	digits = _only_digits(valor)
	if len(digits) != 14:
		return valor or ""
	return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


def _mascarar_cep(valor):
	digits = _only_digits(valor)
	if len(digits) != 8:
		return valor or ""
	return f"{digits[0:5]}-{digits[5:8]}"


def _mascarar_cnj(valor):
	digits = _only_digits(valor)
	if len(digits) != 20:
		return valor or ""
	return (
		f"{digits[0:7]}-{digits[7:9]}.{digits[9:13]}.{digits[13]}.{digits[14:16]}.{digits[16:20]}"
	)


def _mascarar_telefone(valor):
	digits = _only_digits(valor)
	if len(digits) == 11:
		return f"({digits[0:2]}) {digits[2:7]}-{digits[7:11]}"
	if len(digits) == 10:
		return f"({digits[0:2]}) {digits[2:6]}-{digits[6:10]}"
	return valor or ""


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


def _link_label(doctype, name):
	if not name:
		return ""
	if not frappe.db.exists(doctype, name):
		return name
	return frappe.db.get_value(doctype, name, "name") or name


def _get_endereco_principal(cliente):
	if not cliente.enderecos:
		return None
	principal = next((row for row in cliente.enderecos if row.principal), None)
	return principal or cliente.enderecos[0]


def _get_contato_principal(cliente):
	if not cliente.contatos:
		return None
	principal = next(
		(row for row in cliente.contatos if (row.tipo or "").lower() == "principal"),
		None,
	)
	return principal or cliente.contatos[0]


def _get_acordo(servico_name):
	acordo_name = frappe.db.get_value(
		"Acordo de Honorarios Processuais",
		{"servico": servico_name, "docstatus": ["!=", 2]},
		"name",
	)
	if not acordo_name:
		return None
	return frappe.get_doc("Acordo de Honorarios Processuais", acordo_name)


def _montar_endereco_completo(addr):
	if not addr:
		return ""
	partes = []
	logradouro = addr.get("logradouro") or ""
	numero = addr.get("numero") or ""
	if logradouro:
		partes.append(f"{logradouro}{', ' + numero if numero else ''}")
	complemento = addr.get("complemento") or ""
	if complemento:
		partes.append(complemento)
	bairro = addr.get("bairro") or ""
	if bairro:
		partes.append(f"Bairro {bairro}")
	cidade = addr.get("cidade") or ""
	estado = addr.get("estado") or ""
	if cidade or estado:
		partes.append("/".join(filter(None, [cidade, estado])))
	cep = _mascarar_cep(addr.get("cep"))
	if cep:
		partes.append(f"CEP {cep}")
	return " — ".join(partes)


def _get_escritorio_context():
	"""Lê dados do escritório do Single DocType (somente banco, nunca hardcoded)."""
	cfg = frappe.get_single("Configuracao do Escritorio")
	cnpj_raw = cfg.cnpj or ""
	cnpj_fmt = _mascarar_cnpj(cnpj_raw) if _only_digits(cnpj_raw) else cnpj_raw
	return {
		"escritorio_razao_social": cfg.razao_social or "",
		"escritorio_cnpj": cnpj_fmt,
		"escritorio_oab": cfg.oab or "",
		"escritorio_advogada": cfg.advogada or "",
		"escritorio_endereco": cfg.endereco or "",
		"escritorio_registro": cfg.registro_sia or "",
	}


def _build_context(servico_name):
	if not frappe.has_permission("Servico", "read"):
		frappe.throw(_("Sem permissão"), frappe.PermissionError)

	servico = frappe.get_doc("Servico", servico_name)
	cliente = frappe.get_doc("Cliente", servico.cliente)
	addr = _get_endereco_principal(cliente)
	contato = _get_contato_principal(cliente)
	acordo = _get_acordo(servico.name)
	hoje = today()

	tipo_pessoa = cliente.tipo_pessoa or ""
	cpf_raw = cliente.cpf or ""
	cnpj_raw = cliente.cnpj or ""
	cpf_fmt = _mascarar_cpf(cpf_raw) if tipo_pessoa == "Pessoa Física" else ""
	cnpj_fmt = _mascarar_cnpj(cnpj_raw) if tipo_pessoa == "Pessoa Jurídica" else ""

	celular = contato.get("celular") if contato else ""
	telefone_fixo = contato.get("telefone") if contato else ""
	telefone = celular or telefone_fixo or ""
	email = (contato.get("email") if contato else "") or ""

	context = _get_escritorio_context()
	context.update(
		{
			"cliente_nome": cliente.nome or "",
			"cliente_tipo_pessoa": tipo_pessoa,
			"cliente_cpf": cpf_fmt,
			"cliente_cnpj": cnpj_fmt,
			"cliente_rg": cliente.rg or "",
			"cliente_nacionalidade": cliente.nacionalidade or "",
			"cliente_estado_civil": cliente.estado_civil or "",
			"cliente_profissao": cliente.profissao or "",
			"cliente_representante": cliente.representante or "",
			"cliente_cpf_representante": _mascarar_cpf(cliente.cpf_representante),
			"cliente_cargo_representante": cliente.cargo_representante or "",
			"cliente_nome_fantasia": cliente.nome_fantasia or "",
			"endereco_logradouro": addr.logradouro if addr else "",
			"endereco_numero": addr.numero if addr else "",
			"endereco_complemento": addr.complemento if addr else "",
			"endereco_bairro": addr.bairro if addr else "",
			"endereco_cidade": addr.cidade if addr else "",
			"endereco_estado": addr.estado if addr else "",
			"endereco_cep": _mascarar_cep(addr.cep if addr else ""),
			"endereco_completo": _montar_endereco_completo(addr.as_dict() if addr else None),
			"contato_telefone": _mascarar_telefone(telefone),
			"contato_celular": _mascarar_telefone(celular),
			"contato_email": (email or "").lower(),
			"contato_nome": contato.get("nome") if contato else "",
			"telefone_contato": _mascarar_telefone(telefone),
			"servico_titulo": servico.title or "",
			"servico_tipo": servico.tipo or "",
			"servico_status": servico.status or "",
			"servico_numero_processo": _mascarar_cnj(servico.numero_processo),
			"servico_area": servico.area or "",
			"servico_vara": _link_label("Vara", servico.vara),
			"servico_comarca": _link_label("Comarca", servico.comarca),
			"servico_tribunal": _link_label("Tribunal", servico.tribunal),
			"servico_fase_processual": _link_label("Fase Processual", servico.fase_processual),
			"servico_parte_contraria": servico.parte_contraria or "",
			"servico_valor_causa": _formatar_moeda(servico.valor_causa),
			"servico_data_abertura": _formatar_data(servico.data_abertura),
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
	}
	context.update(acordo_defaults)

	if acordo:
		context.update(
			{
				"acordo_modo_honorarios": acordo.modo_honorarios or "",
				"acordo_status": acordo.status or "",
				"acordo_valor_total_do_acordo": _formatar_moeda(acordo.valor_total_do_acordo),
				"acordo_percentual_advogada": _formatar_percentual(acordo.percentual_advogada),
				"acordo_valor_fixo_de_honorarios": _formatar_moeda(acordo.valor_fixo_de_honorarios),
				"acordo_valor_advogada": _formatar_moeda(acordo.valor_advogada),
				"acordo_numero_de_parcelas": cint(acordo.get("número_de_parcelas") or 0) or "",
				"acordo_data_primeira_parcela": _formatar_data(acordo.data_primeira_parcela),
				"acordo_valor_da_parcela": _formatar_moeda(acordo.valor_da_parcela),
				"acordo_total_advogada": _formatar_moeda(acordo.total_advogada),
				"acordo_total_cliente": _formatar_moeda(acordo.total_cliente),
			}
		)

	context.update(
		{
			"servico": servico.name,
			"tipo_servico": context["servico_tipo"],
			"titulo_servico": context["servico_titulo"],
			"numero_processo": context["servico_numero_processo"],
			"area": context["servico_area"],
			"vara": context["servico_vara"],
			"comarca": context["servico_comarca"],
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


def _render_and_attach(servico_name, template_doc, context):
	try:
		from docxtpl import DocxTemplate
	except ImportError:
		frappe.throw(_("Biblioteca docxtpl nao instalada. Contate o administrador."))

	if not template_doc.arquivo:
		frappe.throw(_("Template sem arquivo .docx anexado."))

	file_doc = frappe.get_doc("File", {"file_url": template_doc.arquivo})
	file_path = file_doc.get_full_path()
	if not os.path.exists(file_path):
		frappe.throw(_("Arquivo do template nao encontrado no servidor."))

	tpl = DocxTemplate(file_path)
	tpl.render(context)

	buffer = io.BytesIO()
	tpl.save(buffer)
	buffer.seek(0)

	timestamp = frappe.utils.now_datetime().strftime("%Y%m%d_%H%M%S")
	nome_arquivo = "{0}_{1}_{2}.docx".format(
		re.sub(r"[^\w\-]+", "_", template_doc.titulo).strip("_"),
		servico_name,
		timestamp,
	)

	anexo = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": nome_arquivo,
			"content": buffer.read(),
			"attached_to_doctype": "Servico",
			"attached_to_name": servico_name,
			"is_private": 1,
		}
	)
	anexo.save(ignore_permissions=True)  # File anexado ao Serviço — permissão de write no Serviço já validada

	return {"file_url": anexo.file_url, "file_name": nome_arquivo}


def _parse_template_names(template_names):
	if isinstance(template_names, str):
		template_names = json.loads(template_names or "[]")
	if not isinstance(template_names, list):
		frappe.throw(_("Lista de templates inválida."))
	return [name for name in template_names if name]


@frappe.whitelist()
def gerar_documentos_em_lote(servico_name: str, template_names) -> dict:
	frappe.has_permission("Servico", "read", throw=True)

	nomes = _parse_template_names(template_names)
	if not nomes:
		frappe.throw(_("Selecione ao menos um template."))

	context = _build_context(servico_name)
	gerados = []
	falhas = []

	for template_name in nomes:
		try:
			template_doc = frappe.get_doc("Template Documento", template_name)
			if not template_doc.habilitado:
				raise frappe.ValidationError(_("Template desabilitado: {0}").format(template_name))
			result = _render_and_attach(servico_name, template_doc, context)
			gerados.append(
				{
					"template": template_name,
					"titulo": template_doc.titulo,
					"file_name": result["file_name"],
					"file_url": result["file_url"],
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
	frappe.has_permission("Template Documento", "read", throw=True)
	return frappe.get_all(
		"Template Documento",
		fields=["name", "titulo", "tipo_documento", "descricao"],
		filters={"habilitado": 1},
		order_by="titulo",
	)


@frappe.whitelist()
def get_kits_disponiveis() -> list[dict]:
	frappe.has_permission("Kit de Documentos", "read", throw=True)

	kits = frappe.get_all(
		"Kit de Documentos",
		fields=["name", "titulo", "descricao"],
		filters={"habilitado": 1},
		order_by="titulo",
	)
	if not kits:
		return kits

	kit_names = [kit.name for kit in kits]
	item_rows = frappe.get_all(
		"Kit Documento Item",
		filters={"parent": ["in", kit_names]},
		fields=["parent", "template", "ordem"],
		order_by="parent asc, ordem asc, idx asc",
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
	frappe.has_permission("Template Documento", "read", throw=True)
	return PLACEHOLDER_REFERENCIA
