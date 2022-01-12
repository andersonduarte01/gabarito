from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.Painel.as_view(), name='painel_escola'),
    path('<pk>/editar/', views.EditarEscola.as_view(), name='editar_escola'),
    path('<pk>/usuario/', views.EditarUsuario.as_view(), name='editar_usuario'),
    path('<pk>/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),
]

