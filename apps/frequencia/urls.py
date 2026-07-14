from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [
    path('',                                          views.ListarRegistrosView.as_view(),    name='lista'),
    path('caderneta/',                                views.CadernetaView.as_view(),          name='caderneta'),
    path('iniciar/',                                  views.IniciarAulaView.as_view(),        name='iniciar'),
    path('<int:pk>/',                                 views.DetalheRegistroView.as_view(),    name='detalhe'),
    path('<int:pk>/lancar/',                          views.LancarPresencasView.as_view(),    name='lancar'),
    path('<int:pk>/cancelar/',                        views.CancelarAulaView.as_view(),       name='cancelar'),
    path('presenca/<int:pk>/justificar/',             views.JustificarFaltaView.as_view(),    name='justificar'),
    path('presenca/salvar/',                          views.SalvarPresencaAjaxView.as_view(), name='salvar_presenca'),
    path('aluno/<int:aluno_pk>/<int:ano_letivo_pk>/', views.FrequenciaAlunoView.as_view(),   name='aluno'),
]
