from django.urls import path
from apps.blog import views as blog_views

app_name = 'core'

urlpatterns = [
    path('', blog_views.Index.as_view(), name='inicio'),
    path('sobre/', blog_views.Sobre.as_view(), name='sobre'),
    path('contato/', blog_views.Contato.as_view(), name='contato'),
    path('arquivos/', blog_views.Arquivos.as_view(), name='arquivos'),
    path('arquivos/resultado/', blog_views.PesquisarArquivo.as_view(), name='arquivos_pesquisados'),
    path('biblioteca/', blog_views.Biblioteca.as_view(), name='biblioteca'),
    path('biblioteca/resultado/', blog_views.PesquisarLivro.as_view(), name='livros_pesquisados'),
    path('videoaulas/', blog_views.Eventos.as_view(), name='videos'),
    path('videoaulas/resultado/', blog_views.PesquisarVideo.as_view(), name='videos_pesquisados'),
    path('videoaulas/<str:ano>/<str:sigla>/', blog_views.AnoMateria.as_view(), name='ano_materia'),
]
