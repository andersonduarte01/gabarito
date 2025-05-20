from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('adicionar_sala/', views.AdicionarSala.as_view(), name='adicionar_sala'),
    path('editar_sala/<int:pk>/', views.EditarSala.as_view(), name='edit_sala'),
    path('<int:pk>/deletar/', views.DeletarSala.as_view(), name='deletar_sala'),
]
