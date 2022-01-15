from django.urls import path
from . import views

app_name = 'direcao'

urlpatterns = [
    path('add/', views.CadDirecao.as_view(), name='adicionar'),
    path('lista/', views.DirecaoLista.as_view(), name='lista_direcao'),
    path('<pk>/editar/', views.EditarDirecao.as_view(), name='editar_direcao'),
    path('editar/endereco/<pk>/', views.EnderecoEditar.as_view(), name='editar_endereco'),
    path('<pk>/adicionar/endereco/', views.EnderecoAdicionar.as_view(), name='adicionar_endereco'),
]
