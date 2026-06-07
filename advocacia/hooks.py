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
        "dt": "Notification",
        "filters": [
            [
                "name",
                "in",
                [
                    "Advocacia - Prazo vencendo",
                    "Advocacia - Hearing amanha",
                ],
            ]
        ],
    },
    {
        "dt": "Custom Field",
        "filters": [["dt", "=", "Event"], ["fieldname", "like", "custom_source%"]],
    },
]

app_include_css = [
    "/assets/advocacia/css/list_filters.css",
]

app_include_js = [
    "/assets/advocacia/js/masks.js",
    "/assets/advocacia/js/documentos_placeholders.js",
    "/assets/advocacia/js/painel/utils.js",
    "/assets/advocacia/js/painel/hero.js",
    "/assets/advocacia/js/painel/kpis.js",
    "/assets/advocacia/js/painel/audiencias.js",
    "/assets/advocacia/js/painel/timeline.js",
    "/assets/advocacia/js/painel/financeiro.js",
    "/assets/advocacia/js/painel/refresh.js",
    "/assets/advocacia/js/painel/sections.js",
    "/assets/advocacia/js/painel/handlers.js",
    "/assets/advocacia/js/painel/index.js",
    "/assets/advocacia/js/list_nav.js",
    "/assets/advocacia/js/list_filters.js",
    "/assets/advocacia/js/cliente_from_servico.js",
    "/assets/advocacia/js/timer_global.js",
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
    "advocacia.advocacia.setup.install.after_install",
    "advocacia.advocacia.setup.install.ensure_event_custom_fields",
    "advocacia.advocacia.setup.translations.ensure_doctype_translations",
    "advocacia.advocacia.setup.sidebar.ensure_advocacia_sidebar",
    "advocacia.advocacia.setup.reports.ensure_advocacia_reports",
    "advocacia.advocacia.setup.workspace.ensure_advocacia_workspace",
]
