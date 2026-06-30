from django.db import transaction


def criar(escola, autor, dados):
    from apps.comunicado.models import Comunicado
    turmas = dados.pop('turmas', [])
    comunicado = Comunicado.objects.create(escola=escola, autor=autor, **dados)
    if turmas:
        comunicado.turmas.set(turmas)
    return comunicado


@transaction.atomic
def publicar(comunicado):
    from apps.comunicado.models import DestinatarioComunicado
    from apps.notificacao.models import TipoNotificacao
    from apps.auditoria.models import AcaoAuditoria
    import apps.notificacao.services.notificacao_service as notif_svc
    import apps.auditoria.services.auditoria_service as audit_svc

    if comunicado.publicada:
        return

    comunicado.publicada = True
    comunicado.save(update_fields=['publicada'])

    destinatarios = _resolver_destinatarios(comunicado)
    for usuario in destinatarios:
        notif_svc.criar(
            destinatario=usuario,
            titulo=f'Novo comunicado: {comunicado.titulo}',
            mensagem=comunicado.corpo[:200],
            tipo=TipoNotificacao.COMUNICADO,
        )


def _resolver_destinatarios(comunicado):
    from apps.comunicado.models import DestinatarioComunicado
    from apps.core.models import VinculoEscola
    escola = comunicado.escola

    if comunicado.destinatarios == DestinatarioComunicado.TURMAS:
        turmas = comunicado.turmas.all()
        from apps.aluno.models import MatriculaTurma, SituacaoMatricula
        matriculas = MatriculaTurma.objects.filter(
            turma__in=turmas,
            situacao=SituacaoMatricula.MATRICULADO,
            ativo=True,
        ).select_related('aluno__usuario')
        usuarios = set()
        for mat in matriculas:
            if mat.aluno.usuario_id:
                usuarios.add(mat.aluno.usuario)
        return list(usuarios)

    vinculos = VinculoEscola.objects.filter(escola=escola, ativo=True).select_related('usuario')
    if comunicado.destinatarios == DestinatarioComunicado.RESPONSAVEIS:
        vinculos = vinculos.filter(papeis__tipo='RESPONSAVEL', papeis__ativo=True)
    elif comunicado.destinatarios == DestinatarioComunicado.ALUNOS:
        vinculos = vinculos.filter(papeis__tipo='ALUNO', papeis__ativo=True)

    return list({v.usuario for v in vinculos})


def registrar_leitura(comunicado, usuario):
    from apps.comunicado.models import LeituraComunicado
    LeituraComunicado.objects.get_or_create(comunicado=comunicado, usuario=usuario)


def listar_nao_lidos(usuario, escola):
    from apps.comunicado.models import Comunicado, LeituraComunicado
    lidos_ids = LeituraComunicado.objects.filter(
        usuario=usuario,
    ).values_list('comunicado_id', flat=True)
    return Comunicado.objects.filter(
        escola=escola,
        publicada=True,
    ).exclude(id__in=lidos_ids).order_by('-criado_em')
