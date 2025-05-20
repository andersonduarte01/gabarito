from django.urls import path
from . import views1

app_name = 'arquivos'

urlpatterns = [
    path('', views.Arquivos.as_view(), name='add_arquivo'),
    path('categoria/', views.CategoriaAdd.as_view(), name='add_categoria'),
    path('livro/', views.LivroAdd.as_view(), name='add_livro'),
    path('lista/categorias/', views.CategoriaList.as_view(), name='lista_categoria'),
    path('<int:pk>/categoria/deletar/', views.DeletarCategoria.as_view(), name='deletar_categoria'),
    path('<int:pk>/livro/deletar/', views.DeletarLivro.as_view(), name='deletar_livro'),
    path('<int:pk>/arquivo/deletar/', views.DeletarArquivo.as_view(), name='deletar_arquivo'),
    path('<int:pk>/categoria/atualizar/', views.CategoriaEditar.as_view(), name='editar_categoria'),
    path('<int:pk>/livro/atualizar/', views.LivroEditar.as_view(), name='editar_livro'),
    path('<int:pk>/arquivo/atualizar/', views.ArquivoEditar.as_view(), name='editar_arquivo'),
]
