from django.urls import path
from . import views

app_name = 'funcionario'

urlpatterns = [
    path('painel_dash/', views.DashProfessor.as_view(), name='dash_professor'),
    path('cadastrar/', views.CadastrarProfessor.as_view(), name='adicionar_professor'),
    path('lista/professores/', views.ListaProfessores.as_view(), name='lista_professores'),
    path('<pk>/', views.EditarProfessor.as_view(), name='editar_professor'),
    path('deletar/<pk>/', views.DeletarProfessor.as_view(), name='deletar_professor'),
    path('<slug:slug>/sala/alunos/relatorios/<int:pk>/<str:bimestre>/', views.ListaAlunosrelatorios.as_view(),
         name='alunos_relatorios'),
    path('sala/alunos/<int:id>/', views.ProfAlunos.as_view(), name='prof_sala_alunos'),
]
