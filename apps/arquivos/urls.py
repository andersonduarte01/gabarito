from django.urls import path
from . import views

app_name = 'arquivos'

urlpatterns = [
    # ── Arquivos ─────────────────────────────────────────────────────────────
    path('', views.ArquivoLista.as_view(), name='lista_arquivos'),
    path('pesquisar/', views.PesquisarArquivo.as_view(), name='pesquisar_arquivo'),
    path('adicionar/', views.ArquivoAdd.as_view(), name='add_arquivo'),
    path('<int:pk>/editar/', views.ArquivoEditar.as_view(), name='editar_arquivo'),
    path('<int:pk>/excluir/', views.DeletarArquivo.as_view(), name='deletar_arquivo'),

    # ── Categorias ───────────────────────────────────────────────────────────
    path('categorias/', views.CategoriaList.as_view(), name='lista_categoria'),
    path('categorias/adicionar/', views.CategoriaAdd.as_view(), name='add_categoria'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditar.as_view(), name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.DeletarCategoria.as_view(), name='deletar_categoria'),

    # ── Biblioteca ───────────────────────────────────────────────────────────
    path('biblioteca/', views.BibliotecaLista.as_view(), name='lista_livros'),
    path('biblioteca/pesquisar/', views.PesquisarLivro.as_view(), name='pesquisar_livro'),
    path('biblioteca/adicionar/', views.LivroAdd.as_view(), name='add_livro'),
    path('biblioteca/<int:pk>/editar/', views.LivroEditar.as_view(), name='editar_livro'),
    path('biblioteca/<int:pk>/excluir/', views.DeletarLivro.as_view(), name='deletar_livro'),

    # ── Tutoriais / Vídeos ───────────────────────────────────────────────────
    path('tutoriais/', views.TutoriaisLista.as_view(), name='lista_tutoriais'),
    path('tutoriais/pesquisar/', views.PesquisarVideo.as_view(), name='pesquisar_video'),
    path('tutoriais/adicionar/', views.VideoAdd.as_view(), name='add_video'),
    path('tutoriais/<int:pk>/editar/', views.VideoEditar.as_view(), name='editar_video'),
    path('tutoriais/<int:pk>/excluir/', views.DeletarVideo.as_view(), name='deletar_video'),
    path('tutoriais/<str:ano>/<str:sigla>/', views.AnoMateria.as_view(), name='ano_materia'),
]
