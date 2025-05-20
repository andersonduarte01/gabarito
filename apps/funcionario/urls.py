from django.urls import path
from . import views

app_name = 'funcionario'

urlpatterns = [
    path('cadastrar/', views.CadastrarProfessor.as_view(), name='adicionar_professor'),
    path('lista/professores/', views.ListaProfessores.as_view(), name='lista_professores'),
    path('<pk>/', views.EditarProfessor.as_view(), name='editar_professor'),
    path('deletar/<pk>/', views.DeletarProfessor.as_view(), name='deletar_professor'),
]
