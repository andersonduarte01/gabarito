from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # Roteamento e seleção
    path('redirecionamento/', views.RedirecionarDashboard.as_view(), name='redirecionar'),
    path('selecionar/',       views.SelecionarEscola.as_view(),      name='selecionar'),

    # Dashboard
    path('painel/',          views.DashEscola.as_view(), name='dash_escola'),

    # Perfil e edição
    path('perfil/',          views.PerfilEscola.as_view(),   name='perfil_escola'),
    path('editar/',          views.EditarEscola.as_view(),   name='editar_escola'),
    path('editar/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),

    # Anos letivos
    path('ano-letivo/',                           views.ListaAnosLetivos.as_view(),    name='anos_letivos'),
    path('ano-letivo/novo/',                      views.AdicionarAnoLetivo.as_view(),  name='adicionar_ano_letivo'),
    path('ano-letivo/<int:pk>/editar/',            views.EditarAnoLetivo.as_view(),     name='editar_ano_letivo'),
    path('ano-letivo/<int:pk>/corrente/',          views.DefinirAnoCorrente.as_view(),  name='definir_ano_corrente'),
    path('ano-letivo/<int:pk>/remover/',           views.RemoverAnoLetivo.as_view(),    name='remover_ano_letivo'),

    # Séries
    path('series/',                      views.ListaSeries.as_view(),    name='series'),
    path('series/nova/',                 views.AdicionarSerie.as_view(), name='adicionar_serie'),
    path('series/<int:pk>/editar/',      views.EditarSerie.as_view(),    name='editar_serie'),
    path('series/<int:pk>/remover/',     views.RemoverSerie.as_view(),   name='remover_serie'),

    # Rotas comentadas — dependem de apps desativados temporariamente
    # path('sala/<slug:slug>/alunos/<int:id>/', views.UnidAlunos.as_view(), name='unidade_sala_alunos'),
    # path('frequencia/relatorios/<int:pk>/',   views.FrequenciaRelatorios.as_view(), name='freq_relatorios'),

    # API mobile
    path('api/minhas-escolas/',         views.MinhaEscolaView.as_view(),            name='api_minhas_escolas'),
    path('api/escola/<int:pk>/',        views.EscolaDetalheUpdateView.as_view(),    name='api_escola_detalhe'),
    path('api/escola/<int:pk>/endereco/', views.EnderecoEscolarUpdateView.as_view(), name='api_escola_endereco'),
]
