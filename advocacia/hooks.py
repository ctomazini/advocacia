app_name = "advocacia"
app_title = "Advocacia"
app_publisher = "Charles Tomazini"
app_description = "Gestao juridica para escritorios de advocacia"
app_email = "charles.tomazini@gmail.com"
app_license = "mit"

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["dt", "in", ["Sales Invoice", "Customer"]], ["fieldname", "like", "custom_%"]]
    },
    {
        "dt": "Custom Field",
        "filters": [["name", "=", "Audiencia-link_audiencia"]]
    },
    {
        "dt": "Server Script",
        "filters": [["name", "in", ["Gerar Faturas Acordo", "Atualizar Faturas Acordo", "Contar Faturas Acordo", "Gerar Faturas Atos"]]]
    },
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Advocacia"]]
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
        "advocacia.advocacia.notificacoes.notificar_prazos_diario"
    ]
}
