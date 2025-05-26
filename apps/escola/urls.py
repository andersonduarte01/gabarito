from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('redirecionamento/', views.Redireciona.as_view(), name='redirecionar'),
    path('administrador/', views.DashAdmin.as_view(), name='painel_adm'),
    path('painel_escola/', views.DashEscola.as_view(), name='dash_escola'),
    path('atualizar/<pk>/', views.EditarEscola.as_view(), name='editar_escola'),
    path('frequencia/relatorios/<int:pk>/', views.FrequenciaRelatorios.as_view(), name='freq_relatorios'),
    path('<pk>/atualizar/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),
    path('<pk>/usuario/atualizar/', views.EditarUsuario.as_view(), name='editar_usuario'),
    path('sala/<slug:slug>/alunos/<int:id>/', views.ListAlunos.as_view(), name='unidade_sala_alunos'),
]

