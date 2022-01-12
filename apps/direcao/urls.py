from django.urls import path
from . import views

app_name = 'direcao'

urlpatterns = [
    path('add/', views.CadDirecao.as_view(), name='adicionar'),
    path('lista/', views.DirecaoLista.as_view(), name='lista_direcao')
]
