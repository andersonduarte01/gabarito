from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('<int:pk>/avaliacoes/', views.ListaAvaliacoes.as_view(), name='lista_avaliacoes'),
    path('<int:pk>/alunos/', views.ListarAlunos.as_view(), name='alunos'),
    path('<int:pk>/alunos/avaliacao/', views.AlunosAvaliacao.as_view(), name='alunos_avaliacao'),
    path('add_sala/', views.AdicionarSala.as_view(), name='adicionar_sala'),
    path('editar_sala/<int:pk>/', views.EditarSala.as_view(), name='edit_sala'),
    path('<int:pk>/deletar/', views.DeletarSala.as_view(), name='deletar_sala'),
    path('avaliacoes/', views.ListaAvaliacoes.as_view(), name='avaliacoes_escola'),
    path('', views.ListaSalas.as_view(), name='salas'),
    #Administrador

]
