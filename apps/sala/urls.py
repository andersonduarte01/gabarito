from django.urls import path
from . import views

app_name = 'sala'

urlpatterns = [
    path('', views.ListaSalas.as_view(), name='lista_salas'),
    path('adicionar/', views.AdicionarSala.as_view(), name='adicionar_sala'),
    path('<int:pk>/editar/', views.EditarSala.as_view(), name='editar_sala'),
    path('<int:pk>/deletar/', views.DeletarSala.as_view(), name='deletar_sala'),
]
