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
        "dt": "Client Script",
        "filters": [["name", "=", "Link Audiencia Virtual"]]
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

doctype_js = {
    "Servico": "public/js/servico.js"
}

app_include_js = [
    "/assets/advocacia/js/navegacao.js"
]

scheduler_events = {
    "daily": [
        "advocacia.advocacia.tasks.verificar_parcelas_vencidas",
        "advocacia.advocacia.tasks.notificar_parcelas_vencidas",
        "advocacia.advocacia.tasks.notificar_audiencias_hoje",
        "advocacia.advocacia.notificacoes.notificar_prazos_diario",
    ],
    "weekly": [
        "advocacia.advocacia.tasks.verificar_status_servicos",
    ],
}

doc_events = {
    "Parcela de Honorarios": {
        "on_update": "advocacia.advocacia.tasks.on_parcela_update",
    },
}

after_install = "advocacia.advocacia.setup.install.after_install"

after_migrate = [
    "advocacia.advocacia.setup.reinstalar_istable_doctypes",
    "advocacia.advocacia.setup.install.after_install",
]
