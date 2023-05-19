from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    # path('<int:pk>/<int:sala_id>/', views.AvaliacaoView.as_view(), name='prova'),
    path('adicionar/', views.criarAvaliacao, name='add_avaliacao'),
    path('editar/<int:pk>/', views.EditarAvaliacao.as_view(), name='edit_avaliacao'),
    path('questao_editar/<int:pk>/', views.EditarQuestao.as_view(), name='edit_questao'),
    path('questao/add/', views.AddQuestao.as_view(), name='add_questao'),
    path('lista/', views.ListaAvaliacoes.as_view(), name='lista_avaliacoes'),
    path('questoes/<int:pk>/', views.ListaQuestoes.as_view(), name='lista_questoes'),
    path('questao/<int:pk>/deletar/', views.DeletarQuestao.as_view(), name='deletar_questao'),
    path('lista/avaliacoes/', views.AvaliacaoListEscola.as_view(), name='avaliacoes_escola'),
    path('lista_salas/<int:id_avaliacao>/', views.AvaliacaoListSalas.as_view(), name='avaliacao_salas'),
    path('avaliacao/<int:avaliacao_id>/<int:sala_id>/', views.AvaliacaoAlunos.as_view(), name='avaliar_alunos'),
    # path('iniciar_avaliacao/<int:aluno_id>/<int:avaliacao_id>/', views.responderProvaAluno, name='iniciar_avaliacao'),
    path('prova/<int:aluno_id>/<int:avaliacao_id>/', views.iniciarAvaliacao, name='iniciar_prova'),
    path('prova/<int:gabarito_id>/', views.RefazerAvaliacao, name='refazer_prova'),
    path('prova/gabarito/<int:gabarito_id>/', views.VerGabarito.as_view(), name='ver_gabarito'),
    # # administrador
    # path('<int:sala_id>/<int:avaliacao_id>/<slug:slug>/', views.AvaliacaoAlunosAdm.as_view(), name='avaliar_adm'),
    path('<slug:slug>/<int:aluno_id>/<int:avaliacao_id>/', views.responderProvaAdm, name='avalie_adm'),
]
