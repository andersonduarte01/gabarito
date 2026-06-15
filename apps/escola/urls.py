from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # Roteamento e seleção
    path('redirecionamento/', views.RedirecionarDashboard.as_view(), name='redirecionar'),
    path('selecionar/',       views.SelecionarEscola.as_view(),      name='selecionar'),

    # Dashboard
    path('painel/',          views.DashEscola.as_view(), name='dash_escola'),

    # Edição
    path('editar/',          views.EditarEscola.as_view(),   name='editar_escola'),
    path('editar/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),

    # Rotas comentadas — dependem de apps desativados temporariamente
    # path('sala/<slug:slug>/alunos/<int:id>/', views.UnidAlunos.as_view(), name='unidade_sala_alunos'),
    # path('frequencia/relatorios/<int:pk>/',   views.FrequenciaRelatorios.as_view(), name='freq_relatorios'),

    # API mobile
    path('api/minhas-escolas/',         views.MinhaEscolaView.as_view(),            name='api_minhas_escolas'),
    path('api/escola/<int:pk>/',        views.EscolaDetalheUpdateView.as_view(),    name='api_escola_detalhe'),
    path('api/escola/<int:pk>/endereco/', views.EnderecoEscolarUpdateView.as_view(), name='api_escola_endereco'),
]
