from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.Index.as_view(), name='inicio'),
    path('template/', views.Base.as_view(), name='avaliacao'),
]
