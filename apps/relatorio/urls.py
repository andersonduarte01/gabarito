from django.urls import path

from . import views

app_name = 'relatorio'

urlpatterns = [
    path('',                      views.IndexRelatoriosView.as_view(),    name='index'),
    path('desempenho-turma/',     views.DesempenhoTurmaView.as_view(),    name='desempenho_turma'),
    path('frequencia-turma/',     views.FrequenciaTurmaView.as_view(),    name='frequencia_turma'),
    path('alunos-em-risco/',      views.AlunosEmRiscoView.as_view(),      name='alunos_em_risco'),
    path('boletim-lote/',         views.BoletimLoteView.as_view(),        name='boletim_lote'),
    path('desempenho-professor/', views.DesempenhoProfessorView.as_view(), name='desempenho_professor'),
    path('inadimplencia/',        views.InadimplenciaView.as_view(),      name='inadimplencia'),
    path('extrato-financeiro/',   views.ExtratoFinanceiroView.as_view(),  name='extrato_financeiro'),
]
