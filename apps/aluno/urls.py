from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('<int:pk>/editar/', views.EditarAluno.as_view(), name='editar'),
    path('<int:pk>/deletar/', views.DeletarAluno.as_view(), name='deletar'),
    path('<int:pk>/', views.ProvasView.as_view(), name='provas'),
    path('prova/<int:pk>/', views.ProvaView.as_view(), name='prova'),
]
