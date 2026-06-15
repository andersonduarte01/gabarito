from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Públicas
    path('', views.NoticiaLista.as_view(), name='noticias'),
    path('pesquisar/', views.NoticiaPesquisa.as_view(), name='noticias_pesquisadas'),

    # Gerenciamento (requer autenticação + permissão)
    path('gerenciar/', views.GerenciarNoticias.as_view(), name='gerenciar'),
    path('criar/', views.CriarNoticia.as_view(), name='add_noticia'),
    path('<int:pk>/editar/', views.EditarNoticia.as_view(), name='edit_noticia'),
    path('<int:pk>/excluir/', views.ExcluirNoticia.as_view(), name='excluir'),
    path('<int:pk>/publicar/', views.AlternarStatusNoticia.as_view(), name='publicar'),

    # Detalhe — deve ficar por último para não capturar as rotas acima
    path('<slug:slug>/', views.NoticiaDetalhe.as_view(), name='noticia'),
]
