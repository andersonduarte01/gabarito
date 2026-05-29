from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('', views.ListaAlunos.as_view(), name='lista_alunos'),
    path('cadastrar/', views.CadastrarAluno.as_view(), name='cadastrar_aluno'),
    path('<int:pk>/editar/', views.EditarAluno.as_view(), name='editar_aluno'),
    path('<int:pk>/desativar/', views.DesativarAluno.as_view(), name='desativar_aluno'),
]
