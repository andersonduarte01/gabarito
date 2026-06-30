from django.urls import path

from . import views

app_name = 'comunicado'

urlpatterns = [
    path('',                           views.ListarComunicadosView.as_view(),   name='lista'),
    path('novo/',                      views.CriarComunicadoView.as_view(),     name='criar'),
    path('<int:pk>/',                  views.DetalheComunicadoView.as_view(),   name='detalhe'),
    path('<int:pk>/editar/',           views.EditarComunicadoView.as_view(),    name='editar'),
    path('<int:pk>/publicar/',         views.PublicarComunicadoView.as_view(),  name='publicar'),
    path('<int:pk>/despublicar/',      views.DespublicarComunicadoView.as_view(), name='despublicar'),
    path('<int:pk>/excluir/',          views.ExcluirComunicadoView.as_view(),   name='excluir'),
]
