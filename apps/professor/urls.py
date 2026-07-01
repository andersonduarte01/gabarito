from django.urls import path
from . import views

app_name = 'professor'

urlpatterns = [
    path('dashboard/',   views.DashboardProfessorView.as_view(),  name='dashboard'),
    path('meu-perfil/',  views.MeuPerfilProfessorView.as_view(),  name='meu_perfil'),
    path('',                                             views.ListarProfessoresView.as_view(),  name='lista'),
    path('criar/',                                       views.CriarProfessorView.as_view(),     name='criar'),
    path('<int:pk>/',                                    views.DetalheProfessorView.as_view(),   name='detalhe'),
    path('<int:pk>/editar/',                             views.EditarProfessorView.as_view(),    name='editar'),
    path('<int:pk>/alterar-senha/',                      views.AlterarSenhaProfessorView.as_view(), name='alterar_senha'),
    path('<int:pk>/desativar/',                          views.DesativarProfessorView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',                           views.ReativarProfessorView.as_view(),  name='reativar'),
    path('<int:pk>/formacao/adicionar/',                 views.AdicionarFormacaoView.as_view(),  name='formacao_adicionar'),
    path('<int:pk>/formacao/<int:formacao_pk>/remover/', views.RemoverFormacaoView.as_view(),    name='formacao_remover'),
]
