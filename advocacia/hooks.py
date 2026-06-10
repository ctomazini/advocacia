app_name = "advocacia"
app_title = "Advocacia"
app_publisher = "Charles Tomazini"
app_description = "Gestao juridica para escritorios de advocacia"
app_email = "charles.tomazini@gmail.com"
app_license = "mit"

fixtures = [
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Advocacia"]]
    },
    {
        "dt": "Role",
        "filters": [["name", "in", ["Advocacia User", "Advocacia Manager"]]],
    },
    {
        "dt": "Kanban Board",
        "filters": [["name", "=", "Advocacia Tarefas"]],
    },
    {
        "dt": "Notification",
        "filters": [
            [
                "name",
                "in",
                [
                    "Advocacia - Prazo vencendo",
                    "Advocacia - Hearing amanha",
                    "Advocacia - Parcela vencida",
                    "Advocacia - Tarefa atrasada",
                ],
            ]
        ],
    },
    {
        "dt": "Custom Field",
        "filters": [["dt", "=", "Event"], ["fieldname", "like", "custom_source%"]],
    },
    {
        "dt": "Print Format",
        "filters": [
            [
                "name",
                "in",
                [
                    "Advocacia - Recibo de Honorários",
                    "Advocacia - Resumo do Processo",
                    "Advocacia - Contrato de Honorários",
                ],
            ]
        ],
    },
]

app_include_css = [
    "/assets/advocacia/css/list_filters.css",
    "/assets/advocacia/css/case_hub.css",
]

app_include_js = [
    "/assets/advocacia/js/masks.js",
    "/assets/advocacia/js/documentos_placeholders.js",
    "/assets/advocacia/js/list_nav.js",
    "/assets/advocacia/js/list_filters.js",
    "/assets/advocacia/js/cliente_from_servico.js",
    "/assets/advocacia/js/timer_global.js",
    "/assets/advocacia/js/case_hub.js",
]

importable_doctypes = [
    "Client",
    "Legal Case",
    "Jurisdiction",
    "Case Phase",
    "Court",
]

standard_queries = {
    "Legal Case": "advocacia.advocacia.doctype.legal_case.legal_case.legal_case_query",
}

scheduler_events = {
    "daily": [
        "advocacia.advocacia.tasks.verificar_parcelas_vencidas",
        "advocacia.advocacia.tasks.verificar_despesas_vencidas",
        "advocacia.advocacia.tasks.notificar_parcelas_vencidas",
        "advocacia.advocacia.tasks.notificar_audiencias_hoje",
        "advocacia.advocacia.notificacoes.notificar_prazos_diario",
        "advocacia.advocacia.notificacoes.notificar_tarefas_atrasadas",
    ],
    "weekly": [
        "advocacia.advocacia.tasks.verificar_status_servicos",
    ],
}

doc_events = {
    "Fee Agreement": {
        "on_update": "advocacia.advocacia.financeiro.sincronizar_pagamentos_hook",
    },
    "Fee Installment": {
        "on_update": "advocacia.advocacia.tasks.on_parcela_update",
    },
    "Legal Payment": {
        # Handler único: tarefas + sync honorários/parcela (financeiro.processar_pagamento_on_update)
        "on_update": "advocacia.advocacia.financeiro.processar_pagamento_on_update",
        "on_trash": "advocacia.advocacia.financeiro.on_pagamento_trash",
    },
    "Hearing": {
        "after_insert": "advocacia.advocacia.calendar_sync.sync_audiencia_to_event",
        "on_update": "advocacia.advocacia.calendar_sync.sync_audiencia_to_event",
    },
    "Deadline": {
        "after_insert": "advocacia.advocacia.calendar_sync.sync_prazo_to_event",
        "on_update": "advocacia.advocacia.calendar_sync.sync_prazo_to_event",
    },
}

after_install = "advocacia.advocacia.setup.install.after_install"

after_migrate = [
    "advocacia.advocacia.setup.reinstalar_istable_doctypes",
    "advocacia.advocacia.setup.roles.create_roles",
    "advocacia.advocacia.setup.permissions.setup_permissions",
    "advocacia.advocacia.setup.seed.ensure_seed_data",
    "advocacia.advocacia.setup.install.after_install",
    "advocacia.advocacia.setup.install.ensure_event_custom_fields",
    "advocacia.advocacia.setup.translations.ensure_doctype_translations",
    "advocacia.advocacia.setup.sidebar.ensure_advocacia_sidebar",
    "advocacia.advocacia.setup.reports.ensure_advocacia_reports",
    "advocacia.advocacia.setup.workspace.ensure_advocacia_workspace",
    "advocacia.advocacia.setup.print_formats.ensure_advocacia_print_formats",
]
