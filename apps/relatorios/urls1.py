from django.urls import path
from . import views
app_name = 'relatorios'

urlpatterns = [
    path('<int:aluno>/<slug:slug>/<int:avaliacao_aluno>/', views.RelatorioAluno.as_view(), name='relatorio_aluno'),
    path('<slug:slug>/', views.RelatorioEscola.as_view(), name='relatorio_escola'),
    path('<slug:slug>/<int:avaliacao_id>/<int:pk>/', views.RelatorioSala.as_view(), name='relatorio_sala'),
    path('notas/<int:avaliacao_id>/', views.Notas.as_view(), name='relatorio_geral'),
    path('<slug:slug>/<int:id>/<int:avaliacao_id>/', views.RelatorioAvaliacao.as_view(), name='relatorio_avaliacao'),

]
