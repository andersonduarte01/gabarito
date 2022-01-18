from django.urls import path
from . import views

app_name = 'funcionario'

urlpatterns = [
    path('adicionar/', views.CadastrarFuncionario.as_view(), name='adicionar_funcionario'),
    path('editar/perfil/<pk>/', views.EditarPerfil.as_view(), name='editar_perfil'),
    path('adicionar/perfil/<pk>/', views.PerfilAdicionar.as_view(), name='adicionar_perfil'),
    path('lista/', views.ListaFuncionarios.as_view(), name='lista_funcionarios'),
    path('<pk>/editar/', views.EditarFuncionario.as_view(), name='editar_funcionario'),
    path('editar/endereco/<pk>/', views.EnderecoEditar.as_view(), name='editar_endereco'),
    path('designar/funcao/<pk>/', views.DesignarFuncao.as_view(), name='designar_funcao'),
    path('<pk>/adicionar/endereco/', views.EnderecoAdicionar.as_view(), name='adicionar_endereco'),
    path('<pk>/remover/', views.DeletarDirecao.as_view(), name='deletar_funcionario'),
]
