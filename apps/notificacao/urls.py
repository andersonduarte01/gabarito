from django.urls import path

from . import views

app_name = 'notificacao'

urlpatterns = [
    path('',                views.ListarNotificacoesView.as_view(), name='lista'),
    path('<int:pk>/ler/',   views.MarcarLidaView.as_view(),         name='marcar_lida'),
    path('marcar-todas/',   views.MarcarTodasLidasView.as_view(),   name='marcar_todas'),
]
