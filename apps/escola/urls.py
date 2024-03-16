from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.Painel.as_view(), name='painel_escola'),
    path('<slug:slug>/presenca/', views.PainelPlanilha.as_view(), name='painel_planilha'),
    path('<slug:slug>/<str:data>/presenca/', views.PainelPlanilha00.as_view(), name='painel_planilha_00'),
    path('<slug:slug>/', views.PainelEscola.as_view(), name='painel_da_escola'),
    path('atualizar/<pk>/', views.EditarEscola.as_view(), name='editar_escola'),
    path('<pk>/usuario/', views.EditarUsuario.as_view(), name='editar_usuario'),
    path('<pk>/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),
    ### Administrador ###
    path('<slug:slug>/salas/', views.ListaEscolaSalas.as_view(), name='escola_salas'),
    path('<slug:slug>/sala/<int:id>/alunos', views.ListaEscolaSalaAlunos.as_view(), name='escola_sala_alunos'),
    path('<slug:slug>/professores/', views.ListaEscolaProfessores.as_view(), name='escola_professores'),
    path('<slug:slug>/avaliacoes/', views.EscolaListAvaliacoes.as_view(), name='avaliacoes_escola'),
    path('<slug:slug>/lista_salas/<int:id_avaliacao>/', views.EscolaAvaliacaoListSalas.as_view(), name='escola_avaliacao_salas'),
    path('<slug:slug>/avaliacao/<int:avaliacao_id>/<int:sala_id>/', views.EscolaAvaliacaoAlunos.as_view(), name='escola_avaliar_alunos'),
    path('escolas/pesquisadas/', views.PesquisarEscola.as_view(), name='escolas_pesquisadas'),
    ### Relatorios e registros ###
    path('<slug:slug>/meses/registros/atividades/', views.EscolaRegistroMesesSalas.as_view(), name='escola_registro_meses'),
    path('<slug:slug>/<int:mes>/<int:pk>/mes/registros/atividades/', views.EscolaRegistroMesSala.as_view(), name='escola_registro_mes'),
    path('<slug:slug>/painel/relatorios/<str:bimestre>/', views.EscolaPainelRelatorios.as_view(), name='escola_painel_relatorios'),
    path('<slug:slug>/alunos/relatorios/<int:pk>/<str:bimestre>/', views.EscolaListaAlunosrelatorios.as_view(), name='escola_alunos_relatorios'),
    path('relatorio/observacao/<int:pk>/<str:bimestre>/', views.EscolaRelatorio.as_view(), name='escola_relatorio_aluno'),

]

