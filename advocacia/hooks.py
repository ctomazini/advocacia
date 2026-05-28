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
    }
]

doctype_js = {
    "Servico": "public/js/servico.js"
}

app_include_js = [
    "/assets/advocacia/js/navegacao.js"
]

scheduler_events = {
    "daily": [
        "advocacia.advocacia.notificacoes.notificar_prazos_diario",
]
}

after_migrate = [
    "advocacia.advocacia.setup.reinstalar_istable_doctypes"
]
