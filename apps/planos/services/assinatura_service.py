from datetime import date, timedelta

from django.db import transaction

from apps.core.modulos import MODULOS_OBRIGATORIOS
from apps.planos.models import (
    AssinaturaEscola,
    HistoricoAssinatura,
    Modulo,
    ModuloEscola,
    Plano,
    StatusAssinatura,
)


def trial_valido(assinatura: AssinaturaEscola) -> bool:
    """True se o trial ainda está dentro do prazo de dias."""
    if assinatura.status != StatusAssinatura.TRIAL:
        return False
    prazo = assinatura.data_inicio_trial + timedelta(days=assinatura.duracao_trial_dias)
    return date.today() <= prazo


def modulo_ativo(escola, codigo: str) -> bool:
    """
    Verifica se um módulo está acessível para a escola.
    Módulos obrigatórios: sempre True.
    Trial válido: todos os módulos True.
    Outros: consulta ModuloEscola.
    """
    if codigo in MODULOS_OBRIGATORIOS:
        return True
    try:
        assinatura = escola.assinatura
    except AssinaturaEscola.DoesNotExist:
        return False
    if assinatura.status == StatusAssinatura.TRIAL:
        return trial_valido(assinatura)
    if assinatura.status not in (StatusAssinatura.ATIVA, StatusAssinatura.GRACE):
        return False
    return (
        ModuloEscola.objects
        .filter(assinatura=assinatura, modulo__codigo=codigo, ativo=True)
        .exists()
    )


@transaction.atomic
def iniciar_trial(escola, usuario=None) -> AssinaturaEscola:
    """Cria AssinaturaEscola em TRIAL para uma nova escola."""
    assinatura = AssinaturaEscola.objects.create(
        escola=escola,
        status=StatusAssinatura.TRIAL,
        data_inicio_trial=date.today(),
    )
    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=StatusAssinatura.TRIAL,
        status_novo=StatusAssinatura.TRIAL,
        alterado_por=usuario,
        observacao='Trial iniciado automaticamente.',
    )
    return assinatura


@transaction.atomic
def expirar_trial(assinatura: AssinaturaEscola) -> AssinaturaEscola:
    """TRIAL → TRIAL_EXPIRADO. Chamado pelo command diário ou AlunoService."""
    status_anterior   = assinatura.status
    assinatura.status = StatusAssinatura.TRIAL_EXPIRADO
    assinatura.save(update_fields=['status'])
    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=status_anterior,
        status_novo=StatusAssinatura.TRIAL_EXPIRADO,
        observacao='Trial expirado automaticamente.',
    )
    return assinatura


@transaction.atomic
def ativar(
    assinatura: AssinaturaEscola,
    plano: Plano,
    data_vencimento: date,
    usuario,
    observacao: str = '',
) -> AssinaturaEscola:
    """Ativa (ou renova) assinatura com plano e data de vencimento."""
    status_anterior    = assinatura.status
    plano_anterior     = assinatura.plano

    assinatura.plano           = plano
    assinatura.status          = StatusAssinatura.ATIVA
    assinatura.data_inicio     = date.today()
    assinatura.data_vencimento = data_vencimento
    assinatura.data_grace_fim  = None
    assinatura.ativado_por     = usuario
    assinatura.save()

    _sincronizar_modulos(assinatura, plano)

    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=status_anterior,
        status_novo=StatusAssinatura.ATIVA,
        plano_anterior=plano_anterior,
        plano_novo=plano,
        alterado_por=usuario,
        observacao=observacao,
    )
    return assinatura


@transaction.atomic
def iniciar_grace(assinatura: AssinaturaEscola, usuario, observacao: str = '') -> AssinaturaEscola:
    """ATIVA → GRACE com 15 dias de carência."""
    status_anterior           = assinatura.status
    assinatura.status         = StatusAssinatura.GRACE
    assinatura.data_grace_fim = date.today() + timedelta(days=15)
    assinatura.save(update_fields=['status', 'data_grace_fim'])
    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=status_anterior,
        status_novo=StatusAssinatura.GRACE,
        plano_anterior=assinatura.plano,
        plano_novo=assinatura.plano,
        alterado_por=usuario,
        observacao=observacao or 'Carência iniciada por vencimento da assinatura.',
    )
    return assinatura


@transaction.atomic
def suspender(assinatura: AssinaturaEscola, usuario, observacao: str = '') -> AssinaturaEscola:
    """Qualquer status → SUSPENSA."""
    status_anterior   = assinatura.status
    assinatura.status = StatusAssinatura.SUSPENSA
    assinatura.save(update_fields=['status'])
    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=status_anterior,
        status_novo=StatusAssinatura.SUSPENSA,
        plano_anterior=assinatura.plano,
        plano_novo=assinatura.plano,
        alterado_por=usuario,
        observacao=observacao,
    )
    return assinatura


@transaction.atomic
def cancelar(assinatura: AssinaturaEscola, usuario, observacao: str = '') -> AssinaturaEscola:
    """Encerramento deliberado → CANCELADA."""
    status_anterior   = assinatura.status
    assinatura.status = StatusAssinatura.CANCELADA
    assinatura.save(update_fields=['status'])
    HistoricoAssinatura.objects.create(
        assinatura=assinatura,
        status_anterior=status_anterior,
        status_novo=StatusAssinatura.CANCELADA,
        plano_anterior=assinatura.plano,
        plano_novo=assinatura.plano,
        alterado_por=usuario,
        observacao=observacao,
    )
    return assinatura


# ---------------------------------------------------------------------------
# Interno
# ---------------------------------------------------------------------------

def _sincronizar_modulos(assinatura: AssinaturaEscola, plano: Plano) -> None:
    """Cria/atualiza ModuloEscola conforme módulos do plano."""
    ids_do_plano = set(plano.modulos.values_list('id', flat=True))
    existentes   = {me.modulo_id: me for me in ModuloEscola.objects.filter(assinatura=assinatura)}

    for mid in ids_do_plano:
        if mid in existentes:
            if not existentes[mid].ativo:
                existentes[mid].ativo = True
                existentes[mid].save(update_fields=['ativo'])
        else:
            ModuloEscola.objects.create(assinatura=assinatura, modulo_id=mid, ativo=True)

    for mid, me in existentes.items():
        if mid not in ids_do_plano and me.ativo:
            me.ativo = False
            me.save(update_fields=['ativo'])
