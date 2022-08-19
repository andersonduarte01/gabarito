from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.Index.as_view(), name='inicio'),
    path('contato/', views.Contato.as_view(), name='contato'),
    path('sobre/', views.Sobre.as_view(), name='sobre'),
    path('noticias/', views.Noticias.as_view(), name='noticias'),
    path('eventos/', views.Eventos.as_view(), name='eventos'),
    path('biblioteca/', views.Biblioteca.as_view(), name='biblioteca'),
    path('cursos/', views.Cursos.as_view(), name='cursos'),
]
