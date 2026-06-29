from django.urls import path

from . import views

app_name = 'turma'

urlpatterns = [
    path('',                    views.ListarTurmasView.as_view(),  name='lista'),
    path('criar/',              views.CriarTurmaView.as_view(),    name='criar'),
    path('<int:pk>/',           views.DetalheTurmaView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',    views.EditarTurmaView.as_view(),   name='editar'),
    path('<int:pk>/desativar/', views.DesativarTurmaView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',  views.ReativarTurmaView.as_view(),  name='reativar'),
]
