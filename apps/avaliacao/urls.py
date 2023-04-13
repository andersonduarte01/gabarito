from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    path('<int:pk>/<int:sala_id>/', views.AvaliacaoView.as_view(), name='prova'),
    #path('adicionar/', views.AddAvaliacao.as_view(), name='add_avaliacao'),
    path('adicionar/', views.criarAvaliacao, name='add_avaliacao'),
    path('editar/<int:pk>/', views.EditarAvaliacao.as_view(), name='edit_avaliacao'),
    path('questao/add/', views.AddQuestao.as_view(), name='add_questao'),
    path('lista/', views.ListaAvaliacoes.as_view(), name='lista_avaliacoes'),
    path('questoes/<int:pk>/', views.ListaQuestoes.as_view(), name='lista_questoes'),
    path('<int:pk>/<int:id>/avaliacoes/', views.AvaliacaoList.as_view(), name='avaliacoes_aluno'),
    path('avaliacao/<int:avaliacao_id>/<int:sala_id>/', views.AvaliacaoAlunos.as_view(), name='avaliar'),
    path('avaliar/<int:aluno_id>/<int:avaliacao_id>/', views.responderProva, name='avalie'),
    path('iniciar_avaliacao/<int:aluno_id>/<int:avaliacao_id>/', views.responderProvaAluno, name='iniciar_avaliacao'),
    # administrador
    path('<int:sala_id>/<int:avaliacao_id>/<slug:slug>/', views.AvaliacaoAlunosAdm.as_view(), name='avaliar_adm'),
    path('<slug:slug>/<int:aluno_id>/<int:avaliacao_id>/', views.responderProvaAdm, name='avalie_adm'),
]
