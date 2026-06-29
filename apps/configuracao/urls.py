from django.urls import path

from . import views

app_name = 'configuracao'

urlpatterns = [
    path('academica/',  views.ConfiguracaoAcademicaView.as_view(),  name='academica'),
    path('frequencia/', views.ConfiguracaoFrequenciaView.as_view(), name='frequencia'),
    path('professor/',  views.ConfiguracaoProfessorView.as_view(),  name='professor'),
]
