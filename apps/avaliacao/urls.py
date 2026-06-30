from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    path('',                                                    views.ListarAvaliacoesView.as_view(), name='lista'),
    path('criar/',                                              views.CriarAvaliacaoView.as_view(),   name='criar'),
    path('<int:pk>/',                                           views.DetalheAvaliacaoView.as_view(), name='detalhe'),
    path('<int:pk>/editar/',                                    views.EditarAvaliacaoView.as_view(),  name='editar'),
    path('<int:pk>/publicar/',                                  views.PublicarView.as_view(),         name='publicar'),
    path('<int:pk>/despublicar/',                               views.DespublicarView.as_view(),      name='despublicar'),
    path('<int:pk>/questao/adicionar/',                         views.AdicionarQuestaoView.as_view(), name='questao_adicionar'),
    path('<int:pk>/questao/<int:questao_pk>/remover/',          views.RemoverQuestaoView.as_view(),   name='questao_remover'),
    path('<int:pk>/questao/<int:questao_pk>/opcao/adicionar/',  views.AdicionarOpcaoView.as_view(),   name='opcao_adicionar'),
    path('<int:pk>/exportar-pdf/',                              views.ExportarPdfView.as_view(),      name='exportar_pdf'),
    path('<int:pk>/lancar-notas/',                              views.LancarNotasView.as_view(),      name='lancar_notas'),
]
