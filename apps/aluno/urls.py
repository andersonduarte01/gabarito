from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('adicionar/', views.AddAluno.as_view(), name='adicionar_aluno'),
    path('<int:pk>/editar/', views.EditarAluno.as_view(), name='editar'),
    path('<int:pk>/deletar/', views.delete_view, name='deletar'),
    path('<int:pk>/', views.ProvasView.as_view(), name='provas'),
    path('prova/<int:pk>/', views.ProvaView.as_view(), name='prova'),
    path('resultado_busca/', views.ResultadoPesquisa.as_view(), name='resultado'),
    path('pesquisar/', views.Pesquisar.as_view(), name='pesquisar'),
    path('perfil/aluno/<int:pk>/', views.PerfilAluno.as_view(), name='perfil'),
    path('relatorio/<int:pk>/<int:mes>/perfil/aluno/', views.relatorioAluno, name='relatorio'),
]
