from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('<int:pk>/', views.ListarOpcoes.as_view(), name='opcoes'),
    path('<int:pk>/avaliacoes/', views.ListaAvaliacoes.as_view(), name='lista_avaliacoes'),
    path('<int:pk>/alunos/', views.ListarAlunos.as_view(), name='alunos'),
]
