from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('<int:pk>/', views.ListarOpcoes.as_view(), name='opcoes'),
    path('<int:pk>/avaliacoes/', views.ListaAvaliacoes.as_view(), name='lista_avaliacoes'),
    path('<int:pk>/alunos/', views.ListarAlunos.as_view(), name='alunos'),
    path('add_sala/', views.AdicionarSala.as_view(), name='adicionar_sala'),
    path('editar_sala/<int:pk>/', views.EditarSala.as_view(), name='edit_sala'),
    path('<int:pk>/deletar/', views.DeletarSala.as_view(), name='deletar_sala'),
    path('salas/', views.ListaSalas.as_view(), name='salas'),
    path('add_ano/', views.AdicionarAno.as_view(), name='adicionar_ano'),
    #Administrador
    path('<int:pk>/<slug:slug>/', views.ListaAvaliacoesAdm.as_view(), name='lista_avaliacoes_adm'),
]
