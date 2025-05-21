from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [

    path('<int:sala_id>/registros/atividades/', views.RegistroMesesSalas.as_view(), name='relatorio_meses'),
]
