from django.db import transaction


def criar(escola, autor, dados):
    from apps.agenda.models import Evento
    turmas = dados.pop('turmas', [])
    evento = Evento.objects.create(escola=escola, autor=autor, **dados)
    if turmas:
        evento.turmas.set(turmas)
    return evento


@transaction.atomic
def publicar(evento):
    from apps.notificacao.models import TipoNotificacao
    import apps.notificacao.services.notificacao_service as notif_svc

    if evento.publicada:
        return

    evento.publicada = True
    evento.save(update_fields=['publicada'])

    destinatarios = _resolver_destinatarios(evento)
    for usuario in destinatarios:
        notif_svc.criar(
            destinatario=usuario,
            titulo=f'Novo evento: {evento.titulo}',
            mensagem=f'{evento.data_inicio.strftime("%d/%m/%Y")} — {evento.descricao[:150]}',
            tipo=TipoNotificacao.COMUNICADO,
        )


def _resolver_destinatarios(evento):
    from apps.agenda.models import DestinatarioEvento
    from apps.core.models import VinculoEscola
    escola = evento.escola

    if evento.destinatarios == DestinatarioEvento.TURMAS:
        turmas = evento.turmas.all()
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
    if evento.destinatarios == DestinatarioEvento.RESPONSAVEIS:
        vinculos = vinculos.filter(papeis__tipo='RESPONSAVEL', papeis__ativo=True)
    elif evento.destinatarios == DestinatarioEvento.ALUNOS:
        vinculos = vinculos.filter(papeis__tipo='ALUNO', papeis__ativo=True)

    return list({v.usuario for v in vinculos})


def registrar_leitura(evento, usuario):
    from apps.agenda.models import LeituraEvento
    LeituraEvento.objects.get_or_create(evento=evento, usuario=usuario)
