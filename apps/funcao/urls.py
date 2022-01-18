from django.urls import path
from . import views

app_name = 'funcao'

urlpatterns = [
    path('lista/', views.ListaFuncao.as_view(), name='lista_funcoes'),
    path('adicionar/', views.AdicionarFuncao.as_view(), name='adicionar_funcao'),
    path('atualizar/<pk>/', views.AtualizarFuncao.as_view(), name='atualizar_funcao'),
    path('deletar/<pk>/', views.RemoverFuncao.as_view(), name='remover_funcao'),
]
