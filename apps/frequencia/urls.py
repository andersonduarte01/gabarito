from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [

    path('<int:sala_id>/registros/atividades/', views.RegistroMesesSalas.as_view(), name='relatorio_meses'),
    path('relatorio/observacao/<int:pk>/<str:bimestre>/', views.RelatorioAdd.as_view(), name='relatorio_aluno'),
    path('atualizar/relatorio/<int:pk>/', views.RelatorioUpdate.as_view(), name='relatorio_aluno_up'),
    path('registrar/atividades/<int:sala_id>/', views.ProfessorRegistroMesesSalas.as_view(), name='prof_relatorio_meses'),
    path('registro/atividade/<int:pk>/', views.RegistroAdd.as_view(), name='registro_semanal'),
    path('<int:pk>/mes/', views.FrequenciaMes.as_view(), name='frequencia_mes'),
    path('editar/<int:sala_id>/<str:cal>/up/', views.atualizar_frequencia_diaria, name='editar_frequencia'),
    path('cadastrar/<str:cal>/<int:sala_id>/', views.frequencia_diaria, name='cadastrar_frequencia'),
    path('alterar/registro/<int:pk>', views.RegistroUpdate.as_view(), name='registro_up'),
    path('deletar/registro/<int:pk>/', views.DeletarRegistro.as_view(), name='registro_del'),
]
