from django.urls import path

from . import views

app_name = 'escola'

urlpatterns = [
    path('perfil/',                             views.PerfilEscolaView.as_view(),    name='perfil'),
    path('segmentos/',                          views.SegmentosView.as_view(),       name='segmentos'),
    path('perfil/editar/',                      views.EditarEscolaView.as_view(),    name='editar'),
    path('enderecos/novo/',                     views.AdicionarEnderecoView.as_view(), name='adicionar_endereco'),
    path('enderecos/<int:pk>/editar/',          views.EditarEnderecoView.as_view(),  name='editar_endereco'),
    path('enderecos/<int:pk>/principal/',       views.DefinirPrincipalView.as_view(), name='definir_principal'),
    path('enderecos/<int:pk>/remover/',         views.RemoverEnderecoView.as_view(), name='remover_endereco'),
    path('segmentos/<int:pk>/remover/',         views.RemoverSegmentoView.as_view(), name='remover_segmento'),
]
