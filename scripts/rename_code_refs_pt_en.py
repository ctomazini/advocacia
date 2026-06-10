"""Substitui referências de fieldnames PT→EN em código (py/js/html/fixtures).

Substituição contextual — só troca o token quando aparece como referência de
campo: string exata entre aspas, acesso pontuado (.token), kwarg (token=) ou
chave de objeto JS (token:). Frases PT em _()/__() nunca casam (exigem match
exato da string inteira).

Fora do escopo deste script (tratados manualmente):
- documentos.py (chaves de placeholder docx permanecem PT)
- tokens multi-alvo: data, nome, titulo
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# único alvo global por token; compostos aplicados antes (sort por tamanho)
TOKENS = {
	"tipo_pessoa": "person_type",
	"nome_fantasia": "trade_name",
	"nacionalidade_pj": "representative_nationality",
	"nacionalidade": "nationality",
	"estado_civil": "marital_status",
	"profissao": "occupation",
	"cpf_representante": "representative_cpf",
	"cargo_representante": "representative_role",
	"representante": "representative",
	"observacoes": "remarks",
	"observacao": "remarks",
	"logradouro": "street",
	"numero": "number",
	"complemento": "complement",
	"bairro": "neighborhood",
	"cidade": "city",
	"estado": "state",
	"principal": "is_primary",
	"telefone": "phone",
	"celular": "mobile",
	"descricao": "description",
	"valor_recebido": "received_amount",
	"valor_total_do_acordo": "total_agreement_value",
	"valor_fixo_de_honorarios": "fixed_fee_amount",
	"valor_da_parcela": "installment_amount",
	"valor_advogada": "lawyer_amount",
	"valor_cliente": "client_amount",
	"valor_total": "total_amount",
	"valor_causa": "case_value",
	"valor": "amount",
	"percentual_advogada": "lawyer_percentage",
	"percentual_cliente": "client_percentage",
	"total_advogada": "lawyer_total",
	"total_cliente": "client_total",
	"total_pendente": "pending_total",
	"total_cobrado": "billed_total",
	"total_geral": "grand_total",
	"data_pagamento": "payment_date",
	"data_repasse": "transfer_date",
	"data_recebimento": "received_date",
	"data_vencimento_cobranca": "billing_due_date",
	"data_vencimento": "due_date",
	"data_prazo": "due_date",
	"data_limite": "due_date",
	"data_conclusao": "completion_date",
	"data_abertura": "opening_date",
	"data_primeira_parcela": "first_installment_date",
	"data_hora": "hearing_datetime",
	"proximo_vencimento": "next_due_date",
	"vencimento": "due_date",
	"repassar_cliente": "bill_to_client",
	"forma_pagamento": "payment_method",
	"forma_recebimento": "payment_method",
	"comprovante": "receipt",
	"dias_notificacao": "notification_days",
	"prioridade": "priority",
	"responsavel": "responsible",
	"modo_honorarios": "fee_mode",
	"gerar_parcelas": "generate_installments",
	"gerar_cobranca": "generate_billing",
	"gerar_tarefa": "generate_task",
	"parcela_origem_id": "installment_origin_id",
	"numero_parcela": "installment_number",
	"tipo_origem": "origin_type",
	"sincronizado_em": "synced_at",
	"tipo_documento": "document_type",
	"tipo": "type",
	"modalidade": "modality",
	"resultado": "outcome",
	"status_aud": "status",
	"numero_processo": "case_number",
	"numeracao_legada": "legacy_numbering",
	"parte_contraria": "opposing_party",
	"assunto": "subject",
	"resumo": "summary",
	"proximos_passos": "next_steps",
	"habilitado": "enabled",
	"arquivo": "template_file",
	"ver_placeholders": "show_placeholders",
	"ordem": "display_order",
	"categoria": "category",
	"recorrente": "is_recurring",
	"frequencia": "frequency",
	"razao_social": "company_name",
	"registro_sia": "sia_registration",
	"advogada": "lawyer_name",
	"endereco": "address",
	"hora_inicio": "start_time",
	"hora_fim": "end_time",
	"duracao_minutos": "duration_minutes",
	"duracao_horas": "duration_hours",
	"atividade": "activity",
	"cobravel": "billable",
	"timer_inicio": "timer_start",
	"timer_ativo": "timer_active",
}

EXCLUDE_FILES = {
	"documentos.py",  # chaves de placeholder docx permanecem PT
	"rename_fields_pt_en.py",
	"rename_fieldnames_pt_en.py",
	"rename_code_refs_pt_en.py",
}
EXCLUDE_DIRS = {"node_modules", "__pycache__", "docs", ".git", "doctype"}
# doctype/ JSONs já tratados pelo rename_fieldnames_pt_en.py; py/js de doctype entram:
INCLUDE_DOCTYPE_SUFFIXES = {".py", ".js"}


def iter_files():
	for path in REPO.rglob("*"):
		if not path.is_file() or path.suffix not in {".py", ".js", ".html", ".json"}:
			continue
		rel = path.relative_to(REPO)
		parts = set(rel.parts)
		if parts & {"node_modules", "__pycache__", ".git"}:
			continue
		if rel.parts[0] in {"docs",} or "docs" in parts:
			continue
		if "doctype" in rel.parts and path.suffix == ".json":
			continue  # já tratado
		if path.name in EXCLUDE_FILES:
			continue
		yield path


def build_patterns():
	pats = []
	for old, new in sorted(TOKENS.items(), key=lambda kv: -len(kv[0])):
		pats.append((re.compile(rf'(["\'`]){old}\1'), rf"\g<1>{new}\g<1>"))
		pats.append((re.compile(rf"\.{old}\b"), f".{new}"))
		pats.append((re.compile(rf"\b{old}=(?!=)"), f"{new}="))
	return pats


def build_js_key_patterns():
	pats = []
	for old, new in sorted(TOKENS.items(), key=lambda kv: -len(kv[0])):
		pats.append((re.compile(rf"(?<![\w.$\"'`]){old}(?=\s*:)"), new))
	return pats


def main():
	pats = build_patterns()
	js_pats = build_js_key_patterns()
	touched = []
	for path in iter_files():
		text = orig = path.read_text()
		for pat, repl in pats:
			text = pat.sub(repl, text)
		if path.suffix == ".js":
			for pat, repl in js_pats:
				text = pat.sub(repl, text)
		if text != orig:
			path.write_text(text)
			touched.append(str(path.relative_to(REPO)))
	print(f"{len(touched)} arquivos alterados")
	for t in sorted(touched):
		print(f"  {t}")


if __name__ == "__main__":
	main()
