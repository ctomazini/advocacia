import frappe
from frappe import _
import os
import io


@frappe.whitelist()
def gerar_documento(servico_name, template_name):
    try:
        from docxtpl import DocxTemplate
    except ImportError:
        frappe.throw(_("Biblioteca docxtpl nao instalada. Contate o administrador."))

    servico = frappe.get_doc("Servico", servico_name)
    cliente = frappe.get_doc("Customer", servico.cliente)

    addr = None
    if cliente.customer_primary_address:
        addr = frappe.get_doc("Address", cliente.customer_primary_address)

    contato = None
    if cliente.customer_primary_contact:
        contato = frappe.get_doc("Contact", cliente.customer_primary_contact)

    template_doc = frappe.get_doc("Template Documento", template_name)
    if not template_doc.arquivo:
        frappe.throw(_("Template sem arquivo .docx anexado."))

    file_doc = frappe.get_doc("File", {"file_url": template_doc.arquivo})
    file_path = file_doc.get_full_path()

    if not os.path.exists(file_path):
        frappe.throw(_("Arquivo do template nao encontrado no servidor."))

    hoje = frappe.utils.today()
    context = {
        "servico": servico_name,
        "tipo_servico": servico.tipo or "",
        "titulo_servico": servico.title or "",
        "numero_processo": servico.numero_processo or "",
        "area": servico.area or "",
        "vara": servico.vara or "",
        "comarca": servico.comarca or "",
        "parte_contraria": servico.parte_contraria or "",
        "valor_causa": frappe.utils.fmt_money(servico.valor_causa, currency="BRL") if servico.valor_causa else "",
        "data_abertura": frappe.utils.formatdate(servico.data_abertura, "dd/MM/yyyy") if servico.data_abertura else "",
        "nome": cliente.customer_name or "",
        "cpf": cliente.tax_id or "",
        "cnpj": cliente.tax_id or "",
        "rg": cliente.custom_rg or "",
        "nacionalidade": cliente.custom_nacionalidade or "",
        "estado_civil": cliente.custom_estado_civil or "",
        "profissao": cliente.custom_profissao or "",
        "telefone": cliente.mobile_no or "",
        "email": cliente.email_id or "",
        "endereco": addr.address_line1 if addr else "",
        "complemento": addr.address_line2 if addr and addr.address_line2 else "",
        "bairro": addr.county if addr and addr.county else "",
        "cidade": addr.city if addr else "",
        "estado": addr.state if addr else "",
        "cep": addr.pincode if addr else "",
        "telefone_contato": contato.mobile_no if contato else (cliente.mobile_no or ""),
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
    return frappe.get_all(
        "Template Documento",
        fields=["name", "titulo", "tipo_documento", "descricao"],
        filters={"habilitado": 1},
        order_by="titulo"
    )
