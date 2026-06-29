from django.urls import path

from . import views

app_name = 'materia'

urlpatterns = [
    path('',                                    views.ListarMateriasView.as_view(),   name='lista'),
    path('criar/',                              views.CriarMateriaView.as_view(),     name='criar'),
    path('<int:pk>/',                           views.DetalheMateriaView.as_view(),   name='detalhe'),
    path('<int:pk>/editar/',                    views.EditarMateriaView.as_view(),    name='editar'),
    path('<int:pk>/desativar/',                 views.DesativarMateriaView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',                  views.ReativarMateriaView.as_view(),  name='reativar'),
    path('<int:pk>/vincular-serie/',            views.VincularSerieView.as_view(),    name='vincular_serie'),
    path('<int:pk>/config/<int:config_pk>/desvincular/', views.DesvincularSerieView.as_view(), name='desvincular_serie'),
]
