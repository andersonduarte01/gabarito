from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.Painel.as_view(), name='painel_escola'),
    path('<slug:slug>/presenca/<str:turno>/', views.PainelPlanilha.as_view(), name='painel_planilha'),
    path('<slug:slug>/', views.PainelEscola.as_view(), name='painel_da_escola'),
    path('atualizar/<pk>/', views.EditarEscola.as_view(), name='editar_escola'),
    path('<pk>/usuario/', views.EditarUsuario.as_view(), name='editar_usuario'),
    path('<pk>/endereco/', views.EditarEndereco.as_view(), name='editar_endereco'),
]

