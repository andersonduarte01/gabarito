from django.urls import path
from . import views

app_name = 'funcionario'

urlpatterns = [
    path('painel_dash/', views.DashProfessor.as_view(), name='dash_professor'),
    path('dash/', views.DashFuncionario.as_view(), name='dash_funcionario'),
    path('adicionar/', views.CadastrarFuncionario.as_view(), name='adicionar_funcionario'),
    path('editar/perfil/<pk>/', views.EditarPerfil.as_view(), name='editar_perfil'),
    path('adicionar/perfil/<pk>/', views.PerfilAdicionar.as_view(), name='adicionar_perfil'),
    path('lista/', views.ListaFuncionarios.as_view(), name='lista_funcionarios'),
    path('<pk>/editar/', views.EditarFuncionario.as_view(), name='editar_funcionario'),
    path('editar/endereco/<pk>/', views.EnderecoEditar.as_view(), name='editar_endereco'),
    path('designar/funcao/<pk>/', views.DesignarFuncao.as_view(), name='designar_funcao'),
    path('<pk>/adicionar/endereco/', views.EnderecoAdicionar.as_view(), name='adicionar_endereco'),
    path('<pk>/remover/', views.DeletarDirecao.as_view(), name='deletar_funcionario'),
    #####
    path('cadastrar/professor/', views.CadastrarProfessor.as_view(), name='adicionar_professor'),
    path('professores/', views.ListaProfessores.as_view(), name='lista_professores'),
    path('<int:pk>/professores/', views.ListaProf.as_view(), name='lista_prof'),
    path('professor/<pk>/', views.EditarProfessor.as_view(), name='editar_professor'),
    path('deletar/<pk>/', views.DeletarProfessor.as_view(), name='deletar_professor'),
]
