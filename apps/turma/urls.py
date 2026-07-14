from django.urls import path

from . import views

app_name = 'turma'

urlpatterns = [
    path('',                    views.ListarTurmasView.as_view(),  name='lista'),
    path('criar/',              views.CriarTurmaView.as_view(),    name='criar'),
    path('<int:pk>/',           views.DetalheTurmaView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',    views.EditarTurmaView.as_view(),   name='editar'),
    path('<int:pk>/desativar/', views.DesativarTurmaView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',  views.ReativarTurmaView.as_view(),  name='reativar'),

    # Grade horária
    path('<int:pk>/horario/',                           views.HorarioTurmaView.as_view(),       name='horario'),
    path('<int:pk>/horario/salvar/',                    views.SalvarSlotHorarioView.as_view(),  name='horario_salvar'),
    path('<int:pk>/horario/<int:slot_pk>/remover/',     views.RemoverSlotHorarioView.as_view(), name='horario_remover'),

    # Períodos de aula
    path('periodos/',                                   views.PeriodosAulaView.as_view(),       name='periodos'),
    path('periodos/<int:periodo_pk>/editar/',            views.PeriodosAulaView.as_view(),       name='periodo_editar'),
    path('periodos/<int:periodo_pk>/excluir/',           views.ExcluirPeriodoAulaView.as_view(), name='periodo_excluir'),
]
