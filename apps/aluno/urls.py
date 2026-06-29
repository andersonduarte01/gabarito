from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('',                                     views.ListarAlunosView.as_view(),  name='lista'),
    path('criar/',                               views.CriarAlunoView.as_view(),    name='criar'),
    path('<int:pk>/',                            views.DetalheAlunoView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',                     views.EditarAlunoView.as_view(),   name='editar'),
    path('<int:pk>/desativar/',                  views.DesativarAlunoView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',                   views.ReativarAlunoView.as_view(),  name='reativar'),
    path('<int:pk>/matricular/',                 views.MatricularView.as_view(),    name='matricular'),
    path('matricula/<int:mat_pk>/trocar-turma/', views.TrocarTurmaView.as_view(),   name='trocar_turma'),
    path('matricula/<int:mat_pk>/transferir/',   views.TransferirView.as_view(),    name='transferir'),
    path('matricula/<int:mat_pk>/evadir/',       views.EvadiemView.as_view(),       name='evadir'),
    path('matricula/<int:mat_pk>/concluir/',     views.ConcluirView.as_view(),      name='concluir'),
]
