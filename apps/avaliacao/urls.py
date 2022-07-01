from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    path('<int:pk>/<int:sala_id>/', views.AvaliacaoView.as_view(), name='prova'),
    path('avaliacao/<int:avaliacao_id>/<int:sala_id>/', views.AvaliacaoAlunos.as_view(), name='avaliar'),
    path('avaliar/<int:aluno_id>/<int:avaliacao_id>/', views.responderProva, name='avalie'),
    # administrador
    path('<int:sala_id>/<int:avaliacao_id>/<slug:slug>/', views.AvaliacaoAlunosAdm.as_view(), name='avaliar_adm'),
    path('<slug:slug>/<int:aluno_id>/<int:avaliacao_id>/', views.responderProvaAdm, name='avalie_adm'),
]
