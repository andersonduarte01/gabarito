from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('',          include('apps.core.urls',    namespace='core')),
    path('escola/',   include('apps.escola.urls',  namespace='escola')),
    # Módulos adicionados à medida que são implementados:
    path('planos/',      include('apps.planos.urls',      namespace='planos')),        # M01
    path('onboarding/',    include('apps.onboarding.urls',    namespace='onboarding')),    # M02
    path('configuracao/',   include('apps.configuracao.urls',   namespace='configuracao')),  # M03
    path('notificacoes/',  include('apps.notificacao.urls',   namespace='notificacao')),   # M04
    path('auditoria/',     include('apps.auditoria.urls',     namespace='auditoria')),     # M05
    path('ano-letivo/',    include('apps.ano_letivo.urls',    namespace='ano_letivo')),    # M11
    path('diretor/',       include('apps.diretor.urls',       namespace='diretor')),       # M07
    path('colaboradores/', include('apps.colaborador.urls',    namespace='colaborador')),   # M08
    path('professores/',   include('apps.professor.urls',     namespace='professor')),     # M09
    # path('colaborador/', include('apps.colaborador.urls', namespace='colaborador')),  # M08
    # path('professor/',   include('apps.professor.urls',   namespace='professor')),    # M09
    path('responsaveis/', include('apps.responsavel.urls', namespace='responsavel')), # M10
    # path('ano-letivo/',  include('apps.ano_letivo.urls',  namespace='ano_letivo')),  # M11
    path('series/',      include('apps.serie.urls',       namespace='serie')),        # M12
    path('turmas/',      include('apps.turma.urls',       namespace='turma')),        # M13
    # path('turmas/',      include('apps.turma.urls',       namespace='turma')),        # M13
    path('materias/',    include('apps.materia.urls',     namespace='materia')),      # M14
    path('alunos/',      include('apps.aluno.urls',       namespace='aluno')),         # M15
    path('avaliacoes/',  include('apps.avaliacao.urls',   namespace='avaliacao')),    # M16
    path('boletim/',     include('apps.boletim.urls',     namespace='boletim')),       # M17
    # path('boletim/',     include('apps.boletim.urls',     namespace='boletim')),      # M17
    path('frequencia/',  include('apps.frequencia.urls',  namespace='frequencia')),   # M18
    path('financeiro/',  include('apps.financeiro.urls',  namespace='financeiro')),   # M19
    path('comunicados/', include('apps.comunicado.urls',  namespace='comunicado')),   # M20
    path('agenda/',      include('apps.agenda.urls',      namespace='agenda')),        # M20
    path('relatorios/',  include('apps.relatorio.urls',   namespace='relatorio')),    # M21
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
