from django.urls import path
from . import views

app_name = 'colaborador'

urlpatterns = [
    # Colaboradores
    path('', views.ListaColaboradores.as_view(), name='lista_colaboradores'),
    path('cadastrar/', views.CadastrarColaborador.as_view(), name='cadastrar_colaborador'),
    path('<int:pk>/editar/', views.EditarColaborador.as_view(), name='editar_colaborador'),
    path('<int:pk>/desativar/', views.DesativarColaborador.as_view(), name='desativar_colaborador'),

    # Professores
    path('professores/', views.ListaProfessores.as_view(), name='lista_professores'),
    path('professores/cadastrar/', views.CadastrarProfessor.as_view(), name='cadastrar_professor'),
    path('professores/<int:pk>/editar/', views.EditarProfessor.as_view(), name='editar_professor'),
    path('professores/<int:pk>/desativar/', views.DesativarProfessor.as_view(), name='desativar_professor'),
]
