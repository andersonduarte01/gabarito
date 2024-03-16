from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [
    #path('', views.FreqAtual.as_view(), name='freq'),
    path('adicionar/<int:pk>/', views.FreqDiaria.as_view(), name='add'),
    path('<int:sala_id>/<str:cal>/', views.frequencia_diaria, name='freq_aluno'),
    path('registro/atividade/<int:pk>/<str:data>/', views.RegistroAdd.as_view(), name='registro_aluno'),
    path('alterar/registro/<int:pk>/<str:data>/', views.RegistroUpdate.as_view(), name='registro_up'),
    path('deletar/registro/<int:pk>/', views.DeletarRegistro.as_view(), name='registro_del'),
    path('relatorio/observacao/<int:pk>/<str:bimestre>/', views.RelatorioAdd.as_view(), name='relatorio_aluno'),
    path('atualizar/relatorio/<int:pk>/', views.RelatorioUpdate.as_view(), name='relatorio_aluno_up'),
    path('painel/relatorios/<str:bimestre>/', views.PainelRelatorios.as_view(), name='painel_relatorios'),
    path('alunos/relatorios/<int:pk>/<str:bimestre>/', views.ListaAlunosrelatorios.as_view(), name='alunos_relatorios'),
    path('meses/registros/atividades/', views.RegistroMesesSalas.as_view(), name='relatorio_meses'),
    path('<int:mes>/<int:pk>/mes/registros/atividades/', views.RegistroMesSala.as_view(), name='registro_mes'),
]
