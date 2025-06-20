from django.urls import path
from .views import UsuarioLogadoView, UsuarioCreateView

urlpatterns = [
    path('usuario-logado/', UsuarioLogadoView.as_view(), name='usuario-logado'),
    path('usuario-create/', UsuarioCreateView.as_view(), name='usuario-create'),
]