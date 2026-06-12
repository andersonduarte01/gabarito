from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # Fluxo de tenant
    path('selecionar/', views.SelecionarEscola.as_view(), name='selecionar_escola'),
    path('redirecionamento/', views.Redireciona.as_view(), name='redirecionar'),

    # Dashboards
    path('administrador/', views.DashAdmin.as_view(), name='painel_adm'),
    path('painel/', views.DashEscola.as_view(), name='painel_escola'),

    # Edições
    path('atualizar/<pk>/', views.EditarEscola.as_view(), name='editar_escola'),
    path('<pk>/atualizar/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),
    path('<pk>/usuario/atualizar/', views.EditarUsuario.as_view(), name='editar_usuario'),

    # Relatórios
    path('frequencia/relatorios/<int:pk>/', views.FrequenciaRelatorios.as_view(), name='freq_relatorios'),

    # Alunos
    path('sala/<slug:slug>/alunos/<int:id>/', views.ListAlunos.as_view(), name='unidade_sala_alunos'),

    # Superadmin
    path('superadmin/cadastros/', views.SuperadminCadastros.as_view(), name='superadmin_cadastros'),

    # Gestão de usuários
    path('usuarios/', views.GerenciarUsuarios.as_view(), name='gerenciar_usuarios'),
    path('usuarios/<int:pk>/toggle/', views.ToggleUsuarioAtivo.as_view(), name='toggle_usuario'),
    path('usuarios/<int:pk>/remover/', views.RemoverVinculo.as_view(), name='remover_vinculo'),

    # API
    path('api/minha-escola/', views.EscolaLogadaView.as_view(), name='minha-escola'),
    path('api/editar/minha-escola/', views.UnidadeEscolarUpdateView.as_view(), name='editar-minha-escola'),
    path('api/meu-endereco/', views.EnderecoEscolarUpdateView.as_view(), name='meu-endereco'),
]
