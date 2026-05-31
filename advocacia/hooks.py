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
                    "Advocacia - Audiencia amanha",
                ],
            ]
        ],
    },
]

app_include_js = [
    "/assets/advocacia/js/masks.js",
    "/assets/advocacia/js/navegacao.js",
    "/assets/advocacia/js/servico_link.js",
]

standard_queries = {
    "Servico": "advocacia.advocacia.doctype.servico.servico.servico_query",
}

override_whitelisted_methods = {
    "frappe.desk.search.get_link_title": "advocacia.advocacia.doctype.servico.servico.get_link_title",
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
    "Acordo de Honorarios Processuais": {
        "on_update": "advocacia.advocacia.financeiro.sincronizar_pagamentos_hook",
    },
    "Parcela de Honorarios": {
        "on_update": "advocacia.advocacia.tasks.on_parcela_update",
    },
    "Pagamento": {
        "on_update": [
            "advocacia.advocacia.tasks.on_pagamento_update",
            "advocacia.advocacia.financeiro.on_pagamento_update_honorarios",
        ],
        "on_trash": "advocacia.advocacia.financeiro.on_pagamento_trash",
    },
}

after_install = "advocacia.advocacia.setup.install.after_install"

after_migrate = [
    "advocacia.advocacia.setup.reinstalar_istable_doctypes",
    "advocacia.advocacia.setup.install.after_install",
    "advocacia.advocacia.setup.translations.ensure_doctype_translations",
    "advocacia.advocacia.setup.sidebar.ensure_advocacia_sidebar",
    "advocacia.advocacia.setup.reports.ensure_advocacia_reports",
    "advocacia.advocacia.setup.workspace.ensure_advocacia_workspace",
]
