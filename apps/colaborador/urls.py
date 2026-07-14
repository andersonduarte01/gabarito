from django.urls import path
from . import views

app_name = 'colaborador'

urlpatterns = [
    # Portal do Funcionário
    path('dashboard/',            views.DashboardFuncionarioView.as_view(),  name='dashboard'),
    path('meu-perfil/',           views.MeuPerfilColaboradorView.as_view(),  name='meu_perfil'),
    path('meu-perfil/editar/',    views.EditarMeuPerfilView.as_view(),       name='editar_meu_perfil'),
    path('meu-perfil/endereco/',  views.EditarMeuEnderecoView.as_view(),     name='editar_meu_endereco'),
    path('meu-perfil/senha/',     views.TrocarMinhaSenhaView.as_view(),      name='trocar_minha_senha'),

    # Colaboradores
    path('',                            views.ListarColaboradoresView.as_view(), name='lista'),
    path('criar/',                      views.CriarColaboradorView.as_view(),    name='criar'),
    path('<int:pk>/',                   views.DetalheColaboradorView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',            views.EditarColaboradorView.as_view(),   name='editar'),
    path('<int:pk>/alterar-senha/',     views.AlterarSenhaColaboradorView.as_view(), name='alterar_senha'),
    path('<int:pk>/desativar/',         views.DesativarColaboradorView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',          views.ReativarColaboradorView.as_view(), name='reativar'),

    # Funções Escolares
    path('funcoes/',                    views.ListarFuncoesView.as_view(),       name='funcoes'),
    path('funcoes/criar/',              views.CriarFuncaoView.as_view(),         name='funcao_criar'),
    path('funcoes/<int:pk>/editar/',    views.EditarFuncaoView.as_view(),        name='funcao_editar'),
    path('funcoes/<int:pk>/desativar/',   views.DesativarFuncaoView.as_view(),      name='funcao_desativar'),
    path('funcoes/<int:pk>/reativar/',    views.ReativarFuncaoView.as_view(),       name='funcao_reativar'),
    path('funcoes/<int:pk>/permissoes/',  views.PermissoesFuncaoView.as_view(),     name='funcao_permissoes'),
]
