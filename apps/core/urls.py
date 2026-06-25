from django.urls import path
from . import views
from .views_media import serve_media_protegida

app_name = 'core'

urlpatterns = [
    # Públicas
    path('',         views.Index.as_view(),   name='inicio'),
    path('contato/', views.Contato.as_view(), name='contato'),
    path('sobre/',   views.Sobre.as_view(),   name='sobre'),

    # Roteamento pós-login
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),

    # Seleção de contexto (escola / papel)
    path('selecionar-escola/', views.SelecionarEscolaView.as_view(), name='selecionar_escola'),
    path('selecionar-papel/',  views.SelecionarPapelView.as_view(),  name='selecionar_papel'),

    # Mídia protegida
    path('media/<path:path>', serve_media_protegida, name='media_protegida'),
]
