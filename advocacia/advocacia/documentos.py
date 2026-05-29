import frappe
from frappe import _
import os
import io


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

    # Pega primeiro endereço principal ou o primeiro da lista
    addr = None
    if cliente.enderecos:
        principal = next((e for e in cliente.enderecos if e.principal), None)
        addr = principal or cliente.enderecos[0]

    # Pega primeiro contato ou usa dados diretos do cliente
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

    # Determina telefone — contato ou direto no cliente
    telefone = ""
    if contato:
        telefone = contato.celular or contato.telefone or ""
    else:
        telefone = cliente.celular or cliente.telefone or ""

    context = {
        "servico": servico_name,
        "tipo_servico": servico.tipo or "",
        "titulo_servico": getattr(servico, 'title', '') or "",
        "numero_processo": getattr(servico, 'numero_processo', '') or "",
        "area": getattr(servico, 'area', '') or "",
        "vara": getattr(servico, 'vara', '') or "",
        "comarca": getattr(servico, 'comarca', '') or "",
        "parte_contraria": getattr(servico, 'parte_contraria', '') or "",
        "valor_causa": frappe.utils.fmt_money(servico.valor_causa, currency="BRL") if getattr(servico, 'valor_causa', None) else "",
        "data_abertura": frappe.utils.formatdate(servico.data_abertura, "dd/MM/yyyy") if getattr(servico, 'data_abertura', None) else "",
        # Dados do cliente
        "nome": cliente.nome or "",
        "cpf": cliente.cpf or "",
        "cnpj": cliente.cnpj or "",
        "rg": cliente.rg or "",
        "nacionalidade": cliente.nacionalidade or "",
        "estado_civil": cliente.estado_civil or "",
        "profissao": cliente.profissao or "",
        "telefone": telefone,
        "email": (contato.email if contato and contato.email else cliente.email) or "",
        "representante": cliente.representante or "",
        "cpf_representante": cliente.cpf_representante or "",
        # Endereço
        "endereco": addr.logradouro if addr else "",
        "numero": addr.numero if addr else "",
        "complemento": addr.complemento if addr else "",
        "bairro": addr.bairro if addr else "",
        "cidade": addr.cidade if addr else "",
        "estado": addr.estado if addr else "",
        "cep": addr.cep if addr else "",
        # Datas
        "data_hoje": frappe.utils.formatdate(hoje, "dd/MM/yyyy"),
        "data_hoje_extenso": _formatar_data_extenso(hoje),
    }

    tpl = DocxTemplate(file_path)
    tpl.render(context)

    buffer = io.BytesIO()
    tpl.save(buffer)
    buffer.seek(0)

    nome_arquivo = "{0}_{1}.docx".format(
        template_doc.titulo.replace(" ", "_"),
        servico_name
    )

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": nome_arquivo,
        "content": buffer.read(),
        "attached_to_doctype": "Servico",
        "attached_to_name": servico_name,
        "is_private": 1,
    })
    file_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "file_url": file_doc.file_url,
        "file_name": nome_arquivo,
    }


def _formatar_data_extenso(data_str):
    meses = [
        "", "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    from datetime import datetime
    if isinstance(data_str, str):
        dt = datetime.strptime(data_str, "%Y-%m-%d")
    else:
        dt = data_str
    return "{0} de {1} de {2}".format(dt.day, meses[dt.month], dt.year)


@frappe.whitelist()
def get_templates_disponiveis():
    if not frappe.has_permission("Template Documento", "read"):
        frappe.throw("Sem permissão", frappe.PermissionError)
    return frappe.get_all(
        "Template Documento",
        fields=["name", "titulo", "tipo_documento", "descricao"],
        filters={"habilitado": 1},
        order_by="titulo"
    )
