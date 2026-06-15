from django.urls import path

from . import views

app_name = 'diretor'

urlpatterns = [
    path('meu-perfil/',    views.MeuPerfil.as_view(),    name='meu_perfil'),
    path('editar-perfil/', views.EditarPerfil.as_view(), name='editar_perfil'),
]
