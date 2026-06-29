from datetime import timedelta

from django.utils import timezone


def criar(destinatario, titulo, mensagem, tipo):
    from apps.notificacao.models import Notificacao
    return Notificacao.objects.create(
        destinatario=destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
    )


def marcar_lida(notificacao):
    notificacao.lida = True
    notificacao.save(update_fields=['lida'])


def marcar_todas_lidas(usuario):
    from apps.notificacao.models import Notificacao
    Notificacao.objects.filter(destinatario=usuario, lida=False).update(lida=True)


def listar_nao_lidas(usuario):
    from apps.notificacao.models import Notificacao
    return Notificacao.objects.filter(destinatario=usuario, lida=False)


def listar_todas(usuario):
    from apps.notificacao.models import Notificacao
    return Notificacao.objects.filter(destinatario=usuario)


def limpar_antigas():
    from apps.notificacao.models import Notificacao
    limite = timezone.now() - timedelta(days=60)
    deletadas, _ = Notificacao.objects.filter(lida=True, criado_em__lt=limite).delete()
    return deletadas
