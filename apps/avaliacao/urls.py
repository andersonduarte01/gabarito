from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    path('<int:pk>/<int:sala_id>/', views.AvaliacaoView.as_view(), name='prova'),
    #path('correcao/<int:avaliacao_id>/<int:sala_id>/', views.parametrosGabarito, name='avaliar'),
    path('correcao/<int:avaliacao_id>/<int:sala_id>/', views.responderProva, name='avaliar'),
]
