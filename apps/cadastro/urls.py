from django.urls import path
from . import views

app_name = 'cadastro'

urlpatterns = [
    path('', views.Cadastramento.as_view(), name='cadastramento'),
    #path('', views.Cadastrar.as_view(), name='cadastro_add'),
    path('area/inscricao/', views.PainelUser.as_view(), name='painel_user'),
    path('inicio/', views.CadastroInicio1.as_view(), name='cadastro_inicio'),
    path('documentos/', views.RGView.as_view(), name='cadastro_documentos'),
    path('endereco/', views.Endereco.as_view(), name='cadastro_endereco'),
    path('profissional/', views.Profissional1.as_view(), name='cadastro_profissional'),
    path('home/', views.Profissional1.as_view(), name='painel_user'),
    #path('lotado-autocomplete/', views.UnidadeEscolarAutocomplete.as_view(), name='lotado_autocomplete'),
]
