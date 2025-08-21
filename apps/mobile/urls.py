from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (UsuarioLogadoView, UsuarioCreateView,
                    ChamadaAguardandoDoSolicitanteViewSet, UsuariosDoTecnicoViewSet)

router = DefaultRouter()
router.register(
    r'chamados-tecnico-aguardando-do-solicitante',
    ChamadaAguardandoDoSolicitanteViewSet,
    basename='chamados-tecnico-aguardando-do-solicitante')

router1 = DefaultRouter()
router1.register(r'usuarios-tecnico', UsuariosDoTecnicoViewSet, basename='usuarios-tecnico')


urlpatterns = [
    path('usuario-logado/', UsuarioLogadoView.as_view(), name='usuario-logado'),
    path('usuario-create/', UsuarioCreateView.as_view(), name='usuario-create'),
    path('solicitante/', include(router.urls)),
    path('tecnico/', include(router1.urls)),
]