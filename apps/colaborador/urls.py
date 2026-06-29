from django.urls import path
from . import views

app_name = 'colaborador'

urlpatterns = [
    # Colaboradores
    path('',                            views.ListarColaboradoresView.as_view(), name='lista'),
    path('criar/',                      views.CriarColaboradorView.as_view(),    name='criar'),
    path('<int:pk>/',                   views.DetalheColaboradorView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',            views.EditarColaboradorView.as_view(),   name='editar'),
    path('<int:pk>/desativar/',         views.DesativarColaboradorView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',          views.ReativarColaboradorView.as_view(), name='reativar'),

    # Funções Escolares
    path('funcoes/',                    views.ListarFuncoesView.as_view(),       name='funcoes'),
    path('funcoes/criar/',              views.CriarFuncaoView.as_view(),         name='funcao_criar'),
    path('funcoes/<int:pk>/editar/',    views.EditarFuncaoView.as_view(),        name='funcao_editar'),
    path('funcoes/<int:pk>/desativar/', views.DesativarFuncaoView.as_view(),     name='funcao_desativar'),
    path('funcoes/<int:pk>/reativar/',  views.ReativarFuncaoView.as_view(),      name='funcao_reativar'),
]
