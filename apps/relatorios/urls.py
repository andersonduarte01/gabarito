from django.urls import path
from . import views
app_name = 'relatorios'

urlpatterns = [
    path('<int:aluno>/<slug:slug>/<int:avaliacao_aluno>/', views.RelatorioAluno.as_view(), name='relatorio_aluno'),
    path('<slug:slug>/', views.RelatorioEscola.as_view(), name='relatorio_escola'),
    path('<slug:slug>/<int:pk>/', views.RelatorioSala.as_view(), name='relatorio_sala'),
    path('<slug:slug>/<int:id>/<int:avaliacao_id>/', views.RelatorioAvaliacao.as_view(), name='relatorio_avaliacao'),

]
