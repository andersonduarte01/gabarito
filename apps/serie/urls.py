from django.urls import path

from . import views

app_name = 'serie'

urlpatterns = [
    path('',                       views.ListarSeriesView.as_view(),  name='lista'),
    path('criar/',                 views.CriarSerieView.as_view(),    name='criar'),
    path('<int:pk>/editar/',       views.EditarSerieView.as_view(),   name='editar'),
    path('<int:pk>/desativar/',    views.DesativarSerieView.as_view(), name='desativar'),
    path('<int:pk>/reativar/',     views.ReativarSerieView.as_view(),  name='reativar'),
]
