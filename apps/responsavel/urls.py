from django.urls import path
from . import views

app_name = 'responsavel'

urlpatterns = [
    path('portal/dashboard/', views.DashboardResponsavelView.as_view(), name='portal_dashboard'),
    path('portal/perfil/',    views.PerfilResponsavelView.as_view(),     name='portal_perfil'),
    path('',                                      views.ListarResponsaveisView.as_view(),  name='lista'),
    path('criar/',                                views.CriarResponsavelView.as_view(),    name='criar'),
    path('<int:pk>/',                             views.DetalheResponsavelView.as_view(),  name='detalhe'),
    path('<int:pk>/editar/',                      views.EditarResponsavelView.as_view(),   name='editar'),
    path('<int:pk>/vincular-aluno/',              views.VincularAlunoView.as_view(),       name='vincular_aluno'),
    path('<int:pk>/vinculo/<int:vinculo_pk>/desvincular/', views.DesvincularAlunoView.as_view(), name='desvincular_aluno'),
]
