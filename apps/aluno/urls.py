from django.urls import path
from . import views

app_name = 'aluno'

urlpatterns = [
    path('<int:pk>/editar/', views.EditarAluno.as_view(), name='editar'),
    path('<int:pk>/deletar/', views.delete_view, name='deletar'),
    path('frequencia/relatorio/<int:pk>/<int:mes>/aluno/', views.relatorioFrequencia, name='relatorio'),
    path('registro/relatorio/<int:pk>/aluno/', views.relatorioRegistro, name='relatorio-registro'),

]
