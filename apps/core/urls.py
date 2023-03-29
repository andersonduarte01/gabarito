from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.Index.as_view(), name='inicio'),
    path('contato/', views.Contato.as_view(), name='contato'),
    path('sobre/', views.Sobre.as_view(), name='sobre'),
    path('videosaulas/', views.Eventos.as_view(), name='videos'),
    path('materia/videos/', views.Videos.as_view(), name='videos_m'),
    path('biblioteca/', views.Biblioteca.as_view(), name='biblioteca'),
    path('arquivos/', views.Arquivos.as_view(), name='arquivos'),
    path('resultado_pesquisa/arquivos/', views.PesquisarArquivo.as_view(), name='arquivos_pesquisados'),
    path('biblioteca/livros/', views.PesquisarLivro.as_view(), name='livros_pesquisados'),
    path('videos/resultado/', views.PesquisarVideo.as_view(), name='videos_pesquisados'),
    path('pedagogico/cadastro/', views.SignUpADM.as_view(), name='cad_adm'),
]
