from django.urls import path

from . import views

app_name = 'agenda'

urlpatterns = [
    path('',                      views.ListarEventosView.as_view(),    name='lista'),
    path('novo/',                 views.CriarEventoView.as_view(),      name='criar'),
    path('<int:pk>/',             views.DetalheEventoView.as_view(),    name='detalhe'),
    path('<int:pk>/editar/',      views.EditarEventoView.as_view(),     name='editar'),
    path('<int:pk>/publicar/',    views.PublicarEventoView.as_view(),   name='publicar'),
    path('<int:pk>/despublicar/', views.DespublicarEventoView.as_view(), name='despublicar'),
    path('<int:pk>/excluir/',     views.ExcluirEventoView.as_view(),    name='excluir'),
]
