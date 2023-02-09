from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('adicionar/', views.AddAluno.as_view(), name='adicionar_aluno'),
    path('<int:pk>/editar/', views.editar_aluno, name='editar'),
    path('<int:pk>/deletar/', views.delete_view, name='deletar'),
    path('<int:pk>/', views.ProvasView.as_view(), name='provas'),
    path('prova/<int:pk>/', views.ProvaView.as_view(), name='prova'),
]
