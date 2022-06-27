from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    path('<int:pk>/<int:sala_id>/', views.AvaliacaoView.as_view(), name='prova'),
    #path('correcao/<int:avaliacao_id>/<int:sala_id>/', views.parametrosGabarito, name='avaliar'),
    path('avaliacao/<int:avaliacao_id>/<int:sala_id>/', views.AvaliacaoAlunos.as_view(), name='avaliar'),
    path('avaliar/<int:aluno_id>/<int:avaliacao_id>/', views.responderProva, name='avalie'),
]
