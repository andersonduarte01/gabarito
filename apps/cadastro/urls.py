from django.urls import path
from . import views

app_name = 'cadastro'

urlpatterns = [
    path('', views.Cadastrar.as_view(), name='cadastro_add'),
    path('sucesso/', views.CadastroSucess.as_view(), name='cadastro_ok'),
]
