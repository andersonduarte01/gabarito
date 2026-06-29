from django.urls import path

from . import views

app_name = 'onboarding'

urlpatterns = [
    path('',                              views.ListarEscolasView.as_view(),     name='listar_escolas'),
    path('nova/',                         views.CriarEscolaView.as_view(),       name='criar_escola'),
    path('<int:pk>/reenviar/',            views.ReenviarConviteView.as_view(),   name='reenviar_convite'),
    path('convite/<uuid:token>/',         views.CompletarOnboardingView.as_view(), name='completar'),
    path('link-invalido/',                views.LinkInvalidoView.as_view(),      name='link_invalido'),
]
