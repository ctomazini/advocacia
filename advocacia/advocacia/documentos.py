import io
import os

import frappe
from frappe import _

SKIP_FIELDTYPES = frozenset(
	[
		"Table",
		"Section Break",
		"Column Break",
		"Tab Break",
		"HTML",
		"Button",
		"Heading",
		"Image",
		"Attach",
		"Attach Image",
		"Text Editor",
		"Code",
		"Geolocation",
		"JSON",
	]
)

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


def _add_meta_fields(context, prefix, meta, doc):
	if not doc:
		return
	for field in meta.fields:
		if field.fieldtype in SKIP_FIELDTYPES:
			continue
		val = doc.get(field.fieldname)
		context[f"{prefix}_{field.fieldname}"] = val if val is not None else ""


def _build_context(servico, cliente, addr, contato, hoje):
	context = {}

	for prefix, doc in [("servico", servico), ("cliente", cliente)]:
		if doc:
			_add_meta_fields(context, prefix, doc.meta, doc)

	if addr:
		_add_meta_fields(context, "endereco", frappe.get_meta("Endereco Cliente"), addr)

	if contato:
		_add_meta_fields(context, "contato", frappe.get_meta("Contato Cliente"), contato)

	acordo_name = frappe.db.get_value(
		"Acordo de Honorarios Processuais",
		{"servico": servico.name, "docstatus": ["!=", 2]},
		"name",
	)
	if acordo_name:
		acordo = frappe.get_doc("Acordo de Honorarios Processuais", acordo_name)
		_add_meta_fields(context, "acordo", acordo.meta, acordo)

	if servico.valor_causa:
		context["servico_valor_causa"] = frappe.utils.fmt_money(servico.valor_causa, currency="BRL")
	if servico.data_abertura:
		context["servico_data_abertura"] = frappe.utils.formatdate(servico.data_abertura, "dd/MM/yyyy")

	context["data_hoje"] = frappe.utils.formatdate(hoje, "dd/MM/yyyy")
	context["data_hoje_extenso"] = _formatar_data_extenso(hoje)

	telefone = ""
	email = ""
	if contato:
		telefone = contato.get("celular") or contato.get("telefone") or ""
		email = contato.get("email") or ""

	context.update(
		{
			"servico": servico.name,
			"tipo_servico": servico.tipo or "",
			"titulo_servico": servico.title or "",
			"numero_processo": servico.numero_processo or "",
			"area": servico.area or "",
			"vara": servico.vara or "",
			"comarca": servico.comarca or "",
			"parte_contraria": servico.parte_contraria or "",
			"valor_causa": frappe.utils.fmt_money(servico.valor_causa, currency="BRL")
			if servico.valor_causa
			else "",
			"data_abertura": frappe.utils.formatdate(servico.data_abertura, "dd/MM/yyyy")
			if servico.data_abertura
			else "",
			"nome": cliente.nome or "",
			"cpf": cliente.cpf or "",
			"cnpj": cliente.cnpj or "",
			"rg": cliente.rg or "",
			"nacionalidade": cliente.nacionalidade or "",
			"estado_civil": cliente.estado_civil or "",
			"profissao": cliente.profissao or "",
			"telefone": telefone,
			"email": email,
			"representante": cliente.representante or "",
			"cpf_representante": cliente.cpf_representante or "",
			"endereco": addr.logradouro if addr else "",
			"numero": addr.numero if addr else "",
			"complemento": addr.complemento if addr else "",
			"bairro": addr.bairro if addr else "",
			"cidade": addr.cidade if addr else "",
			"estado": addr.estado if addr else "",
			"cep": addr.cep if addr else "",
			"telefone_contato": telefone,
		}
	)

	return context


@frappe.whitelist()
def gerar_documento(servico_name, template_name):
	if not frappe.has_permission("Servico", "read"):
		frappe.throw("Sem permissão", frappe.PermissionError)
	try:
		from docxtpl import DocxTemplate
	except ImportError:
		frappe.throw(_("Biblioteca docxtpl nao instalada. Contate o administrador."))

	servico = frappe.get_doc("Servico", servico_name)
	cliente = frappe.get_doc("Cliente", servico.cliente)

	addr = None
	if cliente.enderecos:
		principal = next((e for e in cliente.enderecos if e.principal), None)
		addr = principal or cliente.enderecos[0]

	contato = None
	if cliente.contatos:
		contato = cliente.contatos[0]

	template_doc = frappe.get_doc("Template Documento", template_name)
	if not template_doc.arquivo:
		frappe.throw(_("Template sem arquivo .docx anexado."))

	file_doc = frappe.get_doc("File", {"file_url": template_doc.arquivo})
	file_path = file_doc.get_full_path()

	if not os.path.exists(file_path):
		frappe.throw(_("Arquivo do template nao encontrado no servidor."))

	hoje = frappe.utils.today()
	context = _build_context(servico, cliente, addr, contato, hoje)

	tpl = DocxTemplate(file_path)
	tpl.render(context)

	buffer = io.BytesIO()
	tpl.save(buffer)
	buffer.seek(0)

	nome_arquivo = "{0}_{1}.docx".format(
		template_doc.titulo.replace(" ", "_"),
		servico_name,
	)

	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": nome_arquivo,
			"content": buffer.read(),
			"attached_to_doctype": "Servico",
			"attached_to_name": servico_name,
			"is_private": 1,
		}
	)
	file_doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"file_url": file_doc.file_url,
		"file_name": nome_arquivo,
	}


def _formatar_data_extenso(data_str):
	meses = [
		"",
		"janeiro",
		"fevereiro",
		"marco",
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
	from datetime import datetime

	if isinstance(data_str, str):
		dt = datetime.strptime(data_str, "%Y-%m-%d")
	else:
		dt = data_str
	return "{0} de {1} de {2}".format(dt.day, meses[dt.month], dt.year)


@frappe.whitelist()
def get_placeholders_disponiveis():
	"""Retorna todos os placeholders agrupados por entidade, para exibir no UI."""
	grupos = {}

	for doctype, prefix in [
		("Servico", "servico"),
		("Cliente", "cliente"),
		("Endereco Cliente", "endereco"),
		("Contato Cliente", "contato"),
		("Acordo de Honorarios Processuais", "acordo"),
	]:
		meta = frappe.get_meta(doctype)
		campos = []
		for field in meta.fields:
			if field.fieldtype in SKIP_FIELDTYPES:
				continue
			campos.append(
				{
					"placeholder": f"{prefix}_{field.fieldname}",
					"label": field.label or field.fieldname,
					"fieldtype": field.fieldtype,
				}
			)
		grupos[doctype] = campos

	grupos["Aliases Legados"] = [
		{"placeholder": placeholder, "label": placeholder, "fieldtype": "alias"}
		for placeholder in LEGACY_PLACEHOLDERS
	]

	grupos["Data"] = [
		{
			"placeholder": "data_hoje",
			"label": "Data Hoje (dd/MM/yyyy)",
			"fieldtype": "computed",
		},
		{
			"placeholder": "data_hoje_extenso",
			"label": "Data Hoje por Extenso",
			"fieldtype": "computed",
		},
	]

	return grupos


@frappe.whitelist()
def get_templates_disponiveis():
	if not frappe.has_permission("Template Documento", "read"):
		frappe.throw("Sem permissão", frappe.PermissionError)
	return frappe.get_all(
		"Template Documento",
		fields=["name", "titulo", "tipo_documento", "descricao"],
		filters={"habilitado": 1},
		order_by="titulo",
	)
