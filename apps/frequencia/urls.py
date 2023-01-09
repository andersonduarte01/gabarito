from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [
    path('', views.FreqAtual.as_view(), name='freq'),
    path('adicionar/<int:pk>/', views.FreqDiaria.as_view(), name='add'),
]