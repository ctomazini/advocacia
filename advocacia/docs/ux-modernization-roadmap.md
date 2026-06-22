# Modernização UX - App Advocacia

Documento permanente de acompanhamento do projeto de modernização de experiência do usuário.

**Criado:** 2026-06-09
**Última atualização:** 2026-06-09
**App:** `advocacia` (Frappe v16)

---

## Objetivos

* Simplificar a experiência do usuário
* Aplicar o Glossário Oficial Sprint 1A
* Reduzir complexidade percebida
* Melhorar navegação
* Preservar compatibilidade total com o banco de dados

---

## Restrições

Nunca:

* Renomear DocTypes EN
* Renomear Roles
* Renomear Slugs de Relatórios
* Renomear Rotas
* Renomear Placeholders Word
* Alterar Schema
* Alterar Child Tables
* Alterar Dados de Produção

---

## Glossário Oficial Sprint 1A

### Princípios

1. **Singular** = registro / formulário. **Plural** = lista, menu, seção.
2. **Honorários** = contrato de prestação de serviços advocatícios (`Fee Agreement`). **Recebimentos** = parcelas a receber do cliente (`Legal Payment`). **Custas** = despesas processuais (`Court Cost`). **Despesas** = gastos do escritório (`Office Expense`). Termos distintos, não intercambiáveis.
3. **Cobrança de Serviço** (`Service Record` + `Legal Act Item`) = faturamento por atos avulsos, separado de honorários contratuais.
4. Nome interno Frappe (coluna "Nome técnico") **permanece inalterado**.
5. **Recebimento** = dinheiro que ENTRA (do cliente pro escritório). **Pagamento / Despesa** = dinheiro que SAI (do escritório pra fora). Nunca misturar. Nunca usar "Pagamento" para entrada.

### O Modelo Financeiro do Escritório

O escritório tem **duas fontes de receita** e **duas categorias de despesa**.

**RECEITAS (dinheiro que entra):**

Caminho 1 — Honorários contratuais:
Fee Agreement → Gerar Parcelas → Legal Payment (parcelas a receber)

Caminho 2 — Serviços avulsos:
Service Record + Legal Act Item → Sincronizar Cobrança → Legal Payment (cobrança avulsa)

Ambos geram Legal Payment, mas com origens distintas.

**DESPESAS (dinheiro que sai):**

Custas Processuais (Court Cost) — despesa judicial vinculada a processo. Quem arca: Escritório ou Cliente (reembolso).

Despesas do Escritório (Office Expense) — gasto operacional sem vínculo a processo.

### 1. App, módulo e painel

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Aplicativo | `advocacia` | Advocacia |
| Módulo / workspace | `Advocacia` | Advocacia |
| Painel principal | (rota atual) | Painel do Escritório |
| Atalho no menu | — | Painel |

### 2. Seções do menu lateral

| Conceito | Nome oficial |
|----------|--------------|
| Seção operacional diária | Dia a Dia |
| Seção hub do caso/processo | Gestão de Casos |
| Seção financeira | Financeiro |
| Seção analytics | Relatórios |
| Seção cadastros mestre | Cadastros |
| Seção admin | Administração |

### 3. DocTypes — transacionais e operacionais

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Caso / processo (hub) | `Legal Case` | Processo | Processos |
| Cliente | `Client` | Cliente | Clientes |
| Contrato de honorários | `Fee Agreement` | Contrato de Honorários | Contratos de Honorários |
| Parcela a receber do cliente | `Legal Payment` | Recebimento | Recebimentos |
| Audiência | `Hearing` | Audiência | Audiências |
| Prazo processual | `Deadline` | Prazo | Prazos |
| Tarefa interna | `Legal Task` | Tarefa | Tarefas |
| Custa processual | `Court Cost` | Custa Processual | Custas Processuais |
| Cobrança de atos avulsos | `Service Record` | Cobrança de Serviço | Cobranças de Serviço |
| Comunicação com cliente | `Case Communication` | Comunicação | Comunicações |
| Registro de horas | `Time Entry` | Registro de Horas | Registro de Horas |
| Documento do processo | `Case Document` | Documento do Processo | Documentos do Processo |
| Despesa do escritório | `Office Expense` | Despesa do Escritório | Despesas do Escritório |
| Configuração single | `Office Settings` | Configurações do Escritório | Configurações do Escritório |

### 4. DocTypes — cadastros auxiliares

| Conceito | Nome técnico | Nome oficial (registro) | Nome oficial (lista / menu) |
|----------|--------------|-------------------------|----------------------------|
| Comarca | `Jurisdiction` | Comarca | Comarcas |
| Tribunal | `Court` | Tribunal | Tribunais |
| Vara | `Court Branch` | Vara | Varas |
| Fase processual | `Case Phase` | Fase Processual | Fases Processuais |
| Modelo Word | `Document Template` | Modelo de Documento | Modelos de Documento |
| Kit de documentos | `Document Kit` | Kit de Documentos | Kits de Documentos |
| Categoria de documento | `Document Category` | Categoria de Documento | Categorias de Documento |

### 5. Child tables

| Conceito | Nome técnico | Nome oficial |
|----------|--------------|--------------|
| Parcela do contrato | `Fee Installment` | Parcela do Contrato |
| Ato cobrado | `Legal Act Item` | Ato Cobrado |
| Item do kit | `Document Kit Item` | Item do Kit |

### 6. Relatórios

(Auditar slugs reais na Etapa 01 e preencher aqui)

### 7. Abas e painéis dentro do Processo (hub)

| Conceito | Nome oficial |
|----------|--------------|
| Dados do processo | Detalhes |
| Audiências vinculadas | Audiências |
| Prazos processuais | Prazos |
| Tarefas internas | Tarefas |
| Área financeira | Financeiro |
| Parcelas de honorários | Recebimentos de Honorários |
| Cobranças de atos avulsos | Serviços Avulsos |
| Custas do processo | Custas Processuais |
| Comunicações | Comunicações |
| Horas | Horas Trabalhadas |
| Documentos | Documentos do Processo |
| Andamento / fases | Fases do Processo |

### 8. Conceitos de domínio (não são DocTypes)

| Conceito | Nome oficial | Definição | Não confundir com |
|----------|--------------|-----------|-------------------|
| Dinheiro que entra do cliente | Recebimento | Qualquer entrada financeira do cliente | Despesa / Custa |
| Contrato fixo de honorários | Honorários Contratuais | Valor acordado no contrato | Serviço avulso |
| Cobrança por ato individual | Serviço Avulso | Ato cobrado fora do contrato | Honorário contratual |
| Despesa judicial do processo | Custa Processual | Gasto judicial pago pelo escritório | Despesa operacional |
| Gasto do escritório | Despesa do Escritório | Gasto operacional sem processo | Custa processual |
| Quem arca com a custa | Responsável pela Custa | Escritório ou Cliente (reembolso) | — |
| Prazo fatal processual | Prazo | Data limite imposta pelo judiciário | Tarefa |
| Atividade interna do escritório | Tarefa | Ação operacional do escritório | Prazo |

### 9. Campos com vazamento de inglês (mapeamento)

| Campo atual (EN) | DocTypes onde aparece | Nome oficial PT |
|------------------|-----------------------|-----------------|
| `Client` (label) | Legal Case, Hearing, Deadline, Legal Task, Fee Agreement, Legal Payment… | Cliente |
| `Court Branch` (label) | Legal Case, Hearing | Vara |
| `Court` (label) | Legal Case | Tribunal |
| `Case Phase` (label) | Legal Case | Fase Processual |
| `Jurisdiction` (label) | Legal Case | Comarca |
| `Legal Task` (chips/ações) | Painel, Case Communication | Tarefa |
| `Legal Payment` (chips/ações) | Painel | Recebimento |
| `+ Client` (chip painel) | Dashboard | + Cliente |

### 10. Fora do glossário UI (intocáveis neste projeto)

| Elemento | Regra |
|----------|--------|
| DocType `name` EN | Permanece (ex.: `Legal Case`, `Legal Payment`) |
| Slugs de relatório | Permanecem |
| Rota do painel | Permanece |
| Placeholders Word | Permanecem em inglês |
| Roles | Permanecem `Advocacia User` / `Advocacia Manager` |
| Fieldnames EN | Permanecem (renomeação de 114 fieldnames já executada) |

### Textos de ajuda financeiros obrigatórios (implementar nas Etapas 07-09)

**Hub do Processo — aba Financeiro (banner):**
O financeiro do processo tem duas fontes de receita: Honorários Contratuais (valor acordado no Contrato de Honorários, dividido em parcelas geradas automaticamente) e Serviços Avulsos (atos individuais cobrados fora do contrato). Ambos geram Recebimentos para controle. Custas Processuais (taxas, perícias) são despesas do processo, não receita.

**Fee Agreement (intro):**
O Contrato de Honorários define o valor e a forma de cobrança dos serviços advocatícios. Após preencher valores e condições, clique em "Gerar Parcelas" para criar os Recebimentos automaticamente. Modos: Diretos (100% escritório) ou Divisão (advogado/cliente indicado).

**Service Record (intro):**
Registre aqui atos individuais prestados ao cliente cobrados FORA do Contrato de Honorários principal. Exemplos: consulta extra, parecer avulso, diligência não prevista. Após adicionar os atos, clique em "Sincronizar Cobrança" para gerar um Recebimento.

**Legal Payment (intro):**
Este registro representa uma parcela a receber (ou já recebida) do cliente. Origem: gerado automaticamente por Contrato de Honorários ou Cobrança de Serviço, ou criado manualmente para entradas avulsas.

**Court Cost (intro):**
Despesas judiciais vinculadas ao processo: taxas judiciais, custas de perícia, emolumentos, cartório. Indique quem arca (Escritório ou Cliente). Se o cliente reembolsa, registre data e valor do reembolso.

**Tooltips obrigatórios:**
- Botão "Gerar Parcelas": Cria ou atualiza os Recebimentos com base nos valores e datas definidos. Parcelas já recebidas não serão alteradas.
- Botão "Sincronizar Cobrança": Gera (ou atualiza) um Recebimento com o valor total dos atos listados.
- Campo "Sucumbência": Honorários devidos pela parte perdedora. Registre percentual ou valor estimado. Recebimento efetivo depende do resultado do processo.

---

## Registro de Etapas

### Etapa 00 — Criar documentação permanente

**Status:** Concluída
**Data:** 2026-06-09
**Responsável:** Sessão Agent / projeto Advocacia

**Objetivo:** Criar documentação permanente do projeto com glossário completo.

**Arquivos analisados:** Nenhum (etapa de documentação)

**Mudanças realizadas:** Criação deste documento.

**Arquivos criados:** `docs/ux-modernization-roadmap.md`

**Impactos identificados:** Nenhum (zero alteração no app)

**Riscos identificados:** Nenhum

**Testes executados:** Nenhum

**Resultado:** Base normativa pronta para Sprint 1A.

**Pendências:** Etapa 01 (auditoria de aderência ao glossário)

**Próximas etapas:** Etapa 01 — Auditoria de aderência

---

## Decisões Arquiteturais

### DEC-F01
**Contexto:** `Legal Payment` era chamado de "Pagamento" na interface, criando ambiguidade com custas (que são pagamentos que SAEM).
**Decisão:** Nome oficial **Recebimento** (entrada do cliente). Nunca "Pagamento" para dinheiro que entra.
**Motivação:** Eliminar confusão "pagamento = entrada ou saída?".
**Impacto:** translations, sidebar, hub, dashboard, forms, mensagens.

### DEC-F02
**Contexto:** Usuário não entende quando usar Fee Agreement vs Service Record.
**Decisão:** Explicar a diferença DENTRO do app com textos de ajuda. Fee Agreement = contrato; Service Record = atos avulsos fora do contrato. Ambos geram Legal Payment mas com origens distintas.
**Motivação:** Reduzir erro de cadastro.
**Impacto:** intros JS, descriptions JSON, empty states, manual.

### DEC-F03
**Contexto:** "Cobrança de serviços" é longo e ambíguo.
**Decisão:** Singular: **Cobrança de Serviço**. Plural: **Cobranças de Serviço**.
**Motivação:** Alinhado ao padrão singular/plural do glossário.
**Impacto:** sidebar, translations, hub panels.

### DEC-F04
**Contexto:** Botão "Sincronizar Cobrança" é jargão de sistema.
**Decisão:** Manter label, adicionar tooltip explicativo.
**Motivação:** Custo baixo, impacto alto na compreensão.
**Impacto:** JS do form (tooltip).

### DEC-F05
**Contexto:** Custa processual vs Despesa do escritório são conceitos distintos.
**Decisão:** Manter DocTypes separados. Custa no hub do Processo. Despesa só no menu geral.
**Motivação:** Alinhado à contabilidade jurídica real.
**Impacto:** Nenhum estrutural.

### DEC-001
**Contexto:** `Legal Case` exibido como "Serviço" / "Serviços" na interface.
**Decisão:** Nome oficial **Processo** (registro) / **Processos** (lista).
**Motivação:** Advogado pensa em "processo" ou "caso", não "serviço".
**Impacto:** translations, sidebar, workspace, hub, dashboard.

---

## Divergências Encontradas

(Preencher na Etapa 01)

---

## Débitos Técnicos Identificados

(Preencher conforme descobertos)

---

## Mudanças Rejeitadas

### Renomear DocType `Legal Payment` → `Receipt`
**Motivo da rejeição:** Risco crítico. Quebra financial.py, hooks, permissions, testes e dados em `tabLegal Payment`.

### Renomear DocType `Legal Case` → `Lawsuit` ou equivalente
**Motivo da rejeição:** Risco crítico. Hub, controllers, hooks, permissions, 12+ DocTypes satélite com Link.

### Renomear rota do painel
**Motivo da rejeição:** Quebra bookmarks, breadcrumbs, módulos dashboard.

### Traduzir placeholders Word
**Motivo da rejeição:** Invalida todos os templates `.docx` em produção.

### Renomear Roles
**Motivo da rejeição:** Impacta permissions, reports, fixtures, usuários atribuídos.

---

## Checklist de Segurança

- [ ] Nenhum DocType EN alterado
- [ ] Nenhum Role alterado
- [ ] Nenhum Report Slug alterado
- [ ] Nenhuma rota alterada
- [ ] Nenhum placeholder Word alterado
- [ ] Nenhum schema alterado
