from django.urls import path
from . import views

app_name = 'boletim'

urlpatterns = [
    path('',                                                           views.BoletimIndexView.as_view(),          name='index'),
    path('turma/<int:turma_pk>/',                                      views.BoletimTurmaView.as_view(),          name='turma'),
    path('<int:aluno_pk>/<int:ano_letivo_pk>/',                        views.BoletimAlunoView.as_view(),          name='boletim_aluno'),
    path('<int:aluno_pk>/<int:ano_letivo_pk>/pdf/',                    views.BoletimPDFView.as_view(),            name='pdf'),
    path('calcular/turma/<int:turma_pk>/periodo/<int:periodo_pk>/',    views.CalcularPeriodoTurmaView.as_view(),  name='calcular_periodo'),
    path('calcular/turma/<int:turma_pk>/anual/',                       views.CalcularAnoTurmaView.as_view(),      name='calcular_anual'),
    path('conselho/<int:resultado_pk>/',                               views.AprovarConselhoView.as_view(),       name='aprovar_conselho'),
]
