from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.Noticias.as_view(), name='noticias'),
    path('<slug:slug>/', views.Noticia.as_view(), name='noticia'),
    path('adicionar/noticia/', views.AddNoticia.as_view(), name='add_noticia'),
    path('atualizar/noticia/<int:pk>/', views.EditNoticia.as_view(), name='edit_noticia'),
    path('noticias/resultado/', views.ResultadoNoticias.as_view(), name='noticias_pesquisadas'),
]
