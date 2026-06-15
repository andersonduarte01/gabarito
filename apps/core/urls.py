from django.urls import path
from . import views
from .views_media import serve_media_protegida

app_name = 'core'

urlpatterns = [
    path('', views.Index.as_view(), name='inicio'),
    path('contato/', views.Contato.as_view(), name='contato'),
    path('sobre/', views.Sobre.as_view(), name='sobre'),
    path('media/<path:path>', serve_media_protegida, name='media_protegida'),
]
