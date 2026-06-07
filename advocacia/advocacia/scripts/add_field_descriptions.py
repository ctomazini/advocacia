"""Aplica description em campos de DocType JSON do app Advocacia."""

from __future__ import annotations

import json
from pathlib import Path

SKIP_FIELDTYPES = frozenset({"Section Break", "Column Break", "Tab Break", "HTML", "Button"})

DESCRIPTIONS: dict[str, dict[str, str]] = {
	"Legal Case": {
		"client": "Client titular deste serviço ou processo.",
		"tipo": "Consultoria ou Processo Judicial. Define campos e validações do formulário.",
		"title": "Título automático no formato ID — cliente. Atualizado ao salvar.",
		"status": "Em andamento, Arquivado, Suspenso ou Encerrado.",
		"case_phase": "Fase atual do processo conforme cadastro rígido de Fases Processuais.",
		"data_abertura": "Data de abertura do serviço ou distribuição do processo.",
		"numero_processo": "Número CNJ do processo (validado automaticamente). Obrigatório para Processo Judicial.",
		"numeracao_legada": "Número antigo ou interno, se diferente do CNJ.",
		"area": "Área do direito: Cível, Criminal, Trabalhista, etc.",
		"court_branch_link": "Court Branch judicial vinculada (cadastro rígido).",
		"court": "Court competente (cadastro rígido).",
		"jurisdiction": "Jurisdiction onde o processo tramita (cadastro rígido).",
		"parte_contraria": "Nome da parte adversa, quando aplicável.",
		"valor_causa": "Valor atribuído à causa na petição inicial.",
		"observacoes": "Anotações internas sobre o serviço ou processo.",
	},
	"Client": {
		"tipo_pessoa": "Pessoa Física ou Pessoa Jurídica. Define quais documentos são obrigatórios.",
		"nome": "Nome completo (PF) ou razão social (PJ). Aparece como título do registro.",
		"nome_fantasia": "Nome fantasia da empresa (apenas pessoa jurídica).",
		"cpf": "CPF do cliente. Apenas dígitos, validado automaticamente.",
		"rg": "Documento de identidade (pessoa física).",
		"cnpj": "CNPJ do cliente. Apenas dígitos, validado automaticamente.",
		"nacionalidade": "Nacionalidade do cliente (pessoa física).",
		"estado_civil": "Estado civil (pessoa física).",
		"profissao": "Profissão declarada (pessoa física).",
		"representante": "Nome do representante legal (pessoa jurídica).",
		"cpf_representante": "CPF do representante legal, com validação automática.",
		"cargo_representante": "Cargo do representante legal na empresa.",
		"nacionalidade_pj": "Nacionalidade do representante legal.",
		"contacts": "Telefones e e-mails de contato do cliente.",
		"addresses": "Endereços do cliente. Marque um como principal para documentos.",
		"observacoes": "Anotações internas sobre o cliente.",
	},
	"Client Contact": {
		"nome": "Nome da pessoa de contato.",
		"tipo": "Relação com o cliente: Principal, Cônjuge, Responsável ou Outro.",
		"telefone": "Telefone fixo com DDD (10 dígitos).",
		"celular": "Celular com DDD (11 dígitos).",
		"email": "E-mail de contato. Armazenado em minúsculas.",
		"observacao": "Observações sobre este contato.",
	},
	"Client Address": {
		"tipo": "Finalidade: Residencial, Comercial, Correspondência ou Outro.",
		"cep": "CEP do endereço (apenas dígitos).",
		"logradouro": "Rua, avenida ou equivalente.",
		"numero": "Número do imóvel.",
		"complemento": "Complemento (apto, sala, bloco).",
		"bairro": "Bairro.",
		"cidade": "Cidade.",
		"uf": "UF (sigla de dois caracteres).",
		"principal": "Marque o endereço principal usado em documentos gerados.",
	},
	"Legal Payment": {
		"title": "Título automático com ID e descritor.",
		"tipo_origem": "Honorários (Parcela) ou Atos Advocatícios.",
		"fee_agreement": "Acordo de honorários que originou este pagamento (parcelas).",
		"service_record": "Registro de atos vinculado (cobrança de atos).",
		"legal_case": "Serviço ou processo relacionado.",
		"client": "Preenchido automaticamente a partir do serviço ou acordo.",
		"numero_parcela": "Número sequencial da parcela no acordo.",
		"descricao": "Descrição exibida na parcela e nos relatórios.",
		"parcela_origem_id": "Identificador interno para sincronização com parcelas do acordo.",
		"sincronizado_em": "Data e hora da última sincronização automática.",
		"manual_override": "Quando marcado, o sistema não sobrescreve este pagamento na sincronização.",
		"valor": "Valor previsto da parcela ou cobrança.",
		"valor_recebido": "Valor efetivamente recebido.",
		"data_vencimento": "Data de vencimento.",
		"data_recebimento": "Data em que o pagamento foi recebido.",
		"status": "Pendente, Vencido, Recebido, Repassado, Cancelado ou Renegociado.",
		"observacoes": "Observações internas sobre o pagamento.",
		"comprovante": "Comprovante de recebimento anexado.",
	},
	"Fee Agreement": {
		"legal_case": "Serviço ou processo vinculado ao acordo.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"modo_honorarios": "Honorários Diretos ou Repasse de Sucumbência.",
		"status": "Vigente, Quitado ou Cancelado.",
		"valor_total_do_acordo": "Valor total acordado entre as partes.",
		"percentual_advogada": "Percentual da advogada sobre o total (modo repasse).",
		"valor_fixo_de_honorarios": "Valor fixo de honorários (modo misto).",
		"valor_advogada": "Parcela destinada à advogada.",
		"billing_type": "Forma de cálculo: valor fixo, percentual ou misto.",
		"percentual_cliente": "Percentual do cliente sobre o total.",
		"valor_cliente": "Parcela destinada ao cliente (repasse).",
		"calculation_type": "Forma de cálculo da sucumbência: percentual ou valor fixo.",
		"contingency_fee_pct": "Percentual sobre a sucumbência.",
		"contingency_fee_amount": "Valor de honorários de sucumbência.",
		"contingency_fee_status": "Situação da sucumbência: pendente, recebida, etc.",
		"installment_count": "Quantidade de parcelas planejadas.",
		"data_primeira_parcela": "Vencimento da primeira parcela.",
		"valor_da_parcela": "Valor médio por parcela (referência).",
		"fee_installments": "Parcelas do acordo. Ao salvar, o sistema gera ou atualiza os pagamentos.",
		"total_advogada": "Soma das parcelas da advogada. Calculado automaticamente.",
		"total_cliente": "Soma das parcelas do cliente. Calculado automaticamente.",
		"remarks": "Observações contratuais e anotações internas.",
		"title": "Título automático no formato ID — cliente.",
	},
	"Fee Installment": {
		"vencimento": "Data de vencimento da parcela.",
		"valor_total": "Valor total da parcela.",
		"valor_advogada": "Parte da parcela destinada à advogada.",
		"contingency_amount": "Parte referente à sucumbência.",
		"valor_cliente": "Parte repassada ao cliente.",
		"description": "Descrição exibida na parcela.",
		"parcela_origem_id": "Identificador interno para sincronização. Gerado automaticamente.",
		"payment": "Legal Payment vinculado gerado pela sincronização.",
		"status": "Pendente, Vencido, Recebido, Repassado ou Cancelado.",
		"data_recebimento": "Data em que a parcela foi recebida.",
		"data_repasse": "Data do repasse ao cliente, quando aplicável.",
		"forma_recebimento": "Forma de recebimento: PIX, TED, Dinheiro, etc.",
		"observacao": "Observações sobre esta parcela.",
	},
	"Hearing": {
		"legal_case": "Serviço ou processo vinculado à audiência.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"data_hora": "Data e hora da audiência.",
		"status_aud": "Agendada, Realizada, Adiada ou Cancelada.",
		"tipo": "Tipo de audiência: Conciliação, Instrução, etc.",
		"modalidade": "Presencial, Virtual ou Híbrida.",
		"link_virtual": "Link de acesso para audiência virtual ou híbrida.",
		"court_branch": "Court Branch ou local da audiência (cadastro rígido).",
		"resultado": "Resultado ou desfecho da audiência.",
		"observacoes": "Anotações sobre a audiência.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Deadline": {
		"legal_case": "Serviço ou processo vinculado ao prazo.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"data_prazo": "Data fatal do prazo processual.",
		"status": "Pendente, Concluído ou Vencido. Vencido é atualizado automaticamente.",
		"descricao": "Descrição do compromisso ou prazo (ex.: contestação, recurso).",
		"prioridade": "Baixa, Média, Alta ou Urgente — usada em alertas e no painel.",
		"responsavel": "Usuário responsável pelo cumprimento do prazo.",
		"dias_notificacao": "Quantos dias antes do vencimento enviar alerta.",
		"observacoes": "Observações adicionais sobre o prazo.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Legal Task": {
		"legal_case": "Serviço relacionado (opcional).",
		"client": "Preenchido automaticamente a partir do serviço.",
		"titulo": "Descrição curta da tarefa.",
		"status": "Pendente, Em Andamento, Concluída ou Cancelada.",
		"prioridade": "Baixa, Média ou Alta.",
		"data_limite": "Prazo para conclusão da tarefa (opcional).",
		"descricao": "Detalhamento da tarefa e instruções.",
		"responsavel": "Usuário responsável pela execução.",
		"data_conclusao": "Preenchida automaticamente ao concluir a tarefa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Case Communication": {
		"legal_case": "Serviço relacionado à comunicação (opcional).",
		"client": "Client envolvido na comunicação.",
		"data": "Data e hora da comunicação.",
		"tipo": "Canal: Telefone, WhatsApp, E-mail, Reunião, etc.",
		"assunto": "Assunto principal da comunicação.",
		"resumo": "Resumo do que foi tratado.",
		"proximos_passos": "Próximos passos combinados (opcional).",
		"gerar_tarefa": "Marque para criar tarefa automaticamente a partir deste registro.",
		"legal_task": "Legal Task gerada a partir desta comunicação.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Service Record": {
		"legal_case": "Serviço ou processo vinculado aos atos.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"status": "Em aberto, Parcialmente cobrado ou Cobrado.",
		"data_abertura": "Data de abertura do registro de atos.",
		"acts": "Atos advocatícios acumulados para cobrança.",
		"total_pendente": "Soma dos atos pendentes. Calculado automaticamente.",
		"total_cobrado": "Soma dos atos já cobrados. Calculado automaticamente.",
		"total_geral": "Total geral dos atos. Calculado automaticamente.",
		"data_vencimento_cobranca": "Vencimento sugerido ao gerar cobrança dos atos pendentes.",
		"last_payment": "Último pagamento de atos vinculado a este registro.",
		"observacoes": "Observações sobre o registro de atos.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Legal Act Item": {
		"data": "Data do ato praticado.",
		"tipo": "Tipo do ato: Inicial, Contestação, Audiência, etc.",
		"description": "Descrição do ato praticado.",
		"valor": "Valor a cobrar por este ato.",
		"status": "Pendente ou Cobrado.",
		"payment": "Legal Payment vinculado quando o ato foi faturado.",
	},
	"Time Entry": {
		"legal_case": "Serviço onde a atividade foi realizada.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"data": "Data da atividade.",
		"atividade": "Descrição curta da atividade realizada.",
		"categoria": "Categoria da atividade: Reunião, Petição, Pesquisa, etc.",
		"descricao": "Detalhamento complementar da atividade.",
		"cobravel": "Marque se o tempo deve entrar em relatórios de cobrança.",
		"duracao_minutos": "Duração em minutos. Use o timer ou informe manualmente.",
		"duracao_horas": "Duração convertida em horas. Calculada automaticamente.",
		"hora_inicio": "Hora de início (timer).",
		"hora_fim": "Hora de término (timer).",
		"timer_ativo": "Indica se o timer está em execução.",
		"timer_inicio": "Momento em que o timer foi iniciado.",
		"responsavel": "Profissional que registrou a atividade.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Court Cost": {
		"legal_case": "Serviço ou processo vinculado à custa.",
		"descricao": "Descrição da custa ou taxa.",
		"tipo": "Taxa Judicial, Emolumento, Despesa Cartorial, etc.",
		"valor": "Valor da custa em reais.",
		"data_pagamento": "Data em que a custa foi paga.",
		"status": "Pendente, Pago, Repassado ou Cancelado.",
		"repassar_cliente": "Marque se o valor deve ser repassado ao cliente.",
		"data_repasse": "Data do repasse ao cliente.",
		"forma_pagamento": "Forma de pagamento: PIX, TED, Dinheiro, etc.",
		"comprovante": "Comprovante de pagamento anexado.",
		"observacoes": "Observações sobre a custa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Office Expense": {
		"descricao": "Descrição da despesa (ex.: aluguel, internet).",
		"categoria": "Categoria: Aluguel, Salários, Software, etc.",
		"valor": "Valor da despesa em reais.",
		"data_vencimento": "Data de vencimento.",
		"data_pagamento": "Data em que a despesa foi paga.",
		"status": "Pendente, Pago ou Atrasado.",
		"recorrente": "Marque se a despesa se repete periodicamente.",
		"frequencia": "Frequência da recorrência: Mensal, Anual, etc.",
		"proximo_vencimento": "Próximo vencimento calculado (despesas recorrentes).",
		"forma_pagamento": "Forma de pagamento: PIX, TED, Boleto, etc.",
		"comprovante": "Comprovante de pagamento anexado.",
		"observacoes": "Observações sobre a despesa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Jurisdiction": {
		"jurisdiction_name": "Nome único da comarca. Usado como identificador do registro.",
		"uf": "Unidade federativa (UF) da comarca.",
		"city": "Cidade sede da comarca.",
	},
	"Court Branch": {
		"court_branch_name": "Nome único da vara. Usado como identificador do registro.",
		"jurisdiction": "Jurisdiction à qual esta vara pertence.",
		"court_type": "Tipo: Cível, Criminal, Família, Trabalho, Federal ou Juizado Especial.",
	},
	"Court": {
		"court_name": "Nome único do tribunal.",
		"abbreviation": "Sigla oficial (ex.: TJRS, TRT4).",
		"jurisdiction": "Esfera: Estadual, Federal, Trabalho, Superior ou Militar.",
	},
	"Case Phase": {
		"case_phase_name": "Nome da fase (ex.: Conhecimento, Execução).",
		"sort_order": "Ordem de exibição no fluxo processual.",
	},
	"Document Template": {
		"titulo": "Nome do modelo. Identificador único no catálogo.",
		"tipo_documento": "Tipo: Petição, Contrato, Procuração, etc.",
		"descricao": "Descrição do uso deste modelo.",
		"arquivo": "Arquivo .docx com placeholders para geração.",
		"habilitado": "Desmarque para ocultar o modelo na geração de documentos.",
		"ver_placeholders": "Abre a referência de placeholders disponíveis no modelo.",
	},
	"Document Kit": {
		"titulo": "Nome do kit. Identificador único.",
		"descricao": "Descrição do conjunto de modelos incluídos.",
		"habilitado": "Desmarque para desabilitar o kit na geração em lote.",
		"templates": "Modelos de documento incluídos neste kit.",
	},
	"Document Kit Item": {
		"template": "Modelo de documento incluído no kit.",
		"ordem": "Ordem de exibição e geração no kit.",
	},
	"Office Settings": {
		"razao_social": "Razão social do escritório. Usada em documentos gerados.",
		"cnpj": "CNPJ do escritório. Usado em contratos e documentos oficiais.",
		"registro_sia": "Registro no SIA/OAB do escritório.",
		"office_logo": "Logotipo exibido em documentos gerados (opcional).",
		"advogada": "Nome da advogada responsável pelo escritório.",
		"oab": "Número da OAB (apenas dígitos).",
		"default_notify_days": "Dias padrão de antecedência para alertas de prazos.",
		"endereco": "Endereço completo do escritório para documentos.",
		"bank_name": "Nome do banco para dados em contratos e recibos.",
		"bank_agency": "Agência bancária.",
		"bank_account": "Número da conta corrente.",
		"bank_pix": "Chave PIX para recebimentos.",
	},
}

FALLBACK_BY_FIELDTYPE: dict[str, str] = {
	"Link": "Selecione o registro vinculado.",
	"Select": "Escolha a opção adequada ao registro.",
	"Check": "Marque quando a condição se aplicar.",
	"Attach": "Anexe o arquivo correspondente.",
	"Attach Image": "Anexe a imagem correspondente.",
	"Table": "Preencha as linhas da tabela abaixo.",
	"Currency": "Valor em reais (R$).",
	"Percent": "Percentual de 0 a 100.",
	"Date": "Informe a data no formato DD/MM/AAAA.",
	"Datetime": "Informe data e hora.",
	"Int": "Número inteiro.",
	"Float": "Número decimal.",
	"Data": "Texto curto de identificação.",
	"Small Text": "Texto complementar.",
	"Text Editor": "Texto longo com formatação.",
}


def _permlevel_hint(permlevel: int) -> str:
	if permlevel and permlevel > 0:
		return " Visível apenas para Advocacia Manager."
	return ""


def _read_only_hint(read_only: int) -> str:
	if read_only:
		return " Preenchido ou calculado automaticamente pelo sistema."
	return ""


def apply_descriptions(doctype_json_path: Path) -> int:
	with open(doctype_json_path, encoding="utf-8") as f:
		data = json.load(f)

	if data.get("doctype") != "DocType":
		return 0

	doctype_name = data.get("name", "")
	field_map = DESCRIPTIONS.get(doctype_name, {})
	updated = 0

	for field in data.get("fields", []):
		ft = field.get("fieldtype")
		if ft in SKIP_FIELDTYPES:
			continue
		if field.get("description"):
			continue

		fn = field.get("fieldname", "")
		desc = field_map.get(fn)
		if not desc:
			base = FALLBACK_BY_FIELDTYPE.get(ft, "")
			if not base:
				continue
			desc = base
			desc += _read_only_hint(field.get("read_only", 0))
			desc += _permlevel_hint(field.get("permlevel", 0))
		else:
			pl = field.get("permlevel", 0)
			if pl and pl > 0 and "Advocacia Manager" not in desc:
				desc = desc.rstrip(".") + ". Visível apenas para Advocacia Manager."

		field["description"] = desc
		updated += 1

	if updated:
		with open(doctype_json_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=1, ensure_ascii=False)
			f.write("\n")

	return updated


def run():
	"""Entry point for bench execute."""
	import frappe
	from frappe import _

	root = Path(frappe.get_app_path("advocacia")) / "advocacia" / "doctype"
	total = 0
	for path in sorted(root.glob("*/*.json")):
		count = apply_descriptions(path)
		if count:
			frappe.logger().info(f"{path.parent.name}: {count} fields")
			total += count
	frappe.msgprint(_("Descrições aplicadas em {0} campos.").format(total))
	return total


def main() -> None:
	root = Path(__file__).resolve().parents[1] / "doctype"
	total = 0
	for path in sorted(root.glob("*/*.json")):
		count = apply_descriptions(path)
		if count:
			print(f"{path.parent.name}: {count} fields")
			total += count
	print(f"Total: {total} descriptions added")


if __name__ == "__main__":
	main()
