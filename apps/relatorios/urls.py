from django.urls import path
from . import views
app_name = 'relatorios'

urlpatterns = [
    path('', views.GeneratePdf.as_view(), name='ola'),
    path('1/', views.GeneratePdf1.as_view(), name='ola1'),
    path('2/', views.GeneratePdf2.as_view(), name='ola2'),
    path('<slug:slug>/', views.RelatorioEscola.as_view(), name='relatorio_escola'),
]
