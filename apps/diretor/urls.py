from django.urls import path

from . import views

app_name = 'diretor'

urlpatterns = [
    path('',                              views.DashboardView.as_view(),       name='dashboard'),
    path('meu-perfil/',                   views.MeuPerfilView.as_view(),       name='meu_perfil'),
    path('meu-perfil/editar/',            views.EditarPerfilView.as_view(),       name='editar_perfil'),
    path('meu-perfil/endereco/',          views.EditarEnderecoPerfilView.as_view(), name='editar_endereco'),
    path('diretores/',                    views.ListarDiretoresView.as_view(), name='listar_diretores'),
    path('diretores/novo/',               views.CriarDiretorView.as_view(),    name='criar_diretor'),
    path('diretores/<int:pk>/desativar/', views.DesativarDiretorView.as_view(), name='desativar_diretor'),
]
