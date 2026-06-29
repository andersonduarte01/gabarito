from django.urls import path

from . import views

app_name = 'ano_letivo'

urlpatterns = [
    path('',                                                      views.ListarAnoLetivoView.as_view(),  name='lista'),
    path('novo/',                                                  views.CriarAnoLetivoView.as_view(),   name='criar'),
    path('<int:pk>/',                                              views.DetalheAnoLetivoView.as_view(), name='detalhe'),
    path('<int:pk>/iniciar/',                                      views.IniciarAnoLetivoView.as_view(), name='iniciar'),
    path('<int:pk>/encerrar/',                                     views.EncerrarAnoLetivoView.as_view(),name='encerrar'),
    path('<int:pk>/periodos/novo/',                                views.CriarPeriodoView.as_view(),     name='criar_periodo'),
    path('<int:pk>/periodos/<int:periodo_pk>/editar/',             views.EditarPeriodoView.as_view(),    name='editar_periodo'),
    path('<int:pk>/periodos/<int:periodo_pk>/remover/',            views.RemoverPeriodoView.as_view(),   name='remover_periodo'),
]
