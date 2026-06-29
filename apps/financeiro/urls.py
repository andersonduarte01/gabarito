from django.urls import path

from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard
    path('',                              views.DashboardFinanceiroView.as_view(), name='dashboard'),

    # Cobranças
    path('cobrancas/',                    views.ListarCobrancasView.as_view(),     name='lista_cobrancas'),
    path('cobrancas/nova/',               views.CriarCobrancaView.as_view(),       name='criar_cobranca'),
    path('cobrancas/<int:pk>/',           views.DetalheCobrancaView.as_view(),     name='detalhe_cobranca'),
    path('cobrancas/<int:pk>/pagar/',     views.PagarManualView.as_view(),         name='pagar_cobranca'),
    path('cobrancas/<int:pk>/cancelar/',  views.CancelarCobrancaView.as_view(),    name='cancelar_cobranca'),

    # Geração em massa
    path('gerar/turma/',                  views.GerarPorTurmaView.as_view(),       name='gerar_turma'),
    path('gerar/escola/',                 views.GerarPorEscolaView.as_view(),      name='gerar_escola'),

    # Planos
    path('planos/',                       views.ListarPlanosView.as_view(),        name='lista_planos'),
    path('planos/novo/',                  views.CriarPlanoView.as_view(),          name='criar_plano'),
    path('planos/<int:pk>/editar/',       views.EditarPlanoView.as_view(),         name='editar_plano'),

    # Webhook
    path('webhook/mercadopago/',          views.WebhookMercadoPagoView.as_view(),  name='webhook_mp'),
]
