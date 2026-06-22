from django.urls import path
from . import views

app_name = 'turma'

urlpatterns = [
    # Turmas
    path('',                   views.ListaTurmas.as_view(),    name='lista_turmas'),
    path('nova/',              views.AdicionarTurma.as_view(), name='adicionar_turma'),
    path('<int:pk>/',          views.DetalhesTurma.as_view(),  name='detalhe_turma'),
    path('<int:pk>/editar/',   views.EditarTurma.as_view(),    name='editar_turma'),
    path('<int:pk>/remover/',  views.RemoverTurma.as_view(),   name='remover_turma'),

]
