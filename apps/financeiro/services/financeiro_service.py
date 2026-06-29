import logging
from datetime import date

from django.db import transaction
from django.utils import timezone

from apps.financeiro.models import CobrancaAluno, GatewayCobranca, PlanoFinanceiro, StatusCobranca

logger = logging.getLogger(__name__)


def _responsavel_financeiro(aluno):
    vinculo = (
        aluno.responsaveis
        .filter(responsavel_financeiro=True, ativo=True)
        .select_related('responsavel')
        .first()
    )
    return vinculo.responsavel if vinculo else None


@transaction.atomic
def gerar_cobranca_aluno(aluno, dados: dict, criado_por) -> CobrancaAluno:
    """
    dados: descricao, valor, vencimento, [plano_financeiro], [gateway]
    """
    responsavel = dados.get('responsavel_financeiro') or _responsavel_financeiro(aluno)
    cobranca = CobrancaAluno.objects.create(
        aluno=aluno,
        responsavel_financeiro=responsavel,
        plano_financeiro=dados.get('plano_financeiro'),
        descricao=dados['descricao'],
        valor=dados['valor'],
        vencimento=dados['vencimento'],
        status=StatusCobranca.PENDENTE,
        gateway=dados.get('gateway', GatewayCobranca.MANUAL),
        criado_por=criado_por,
    )
    _registrar_auditoria(criado_por, 'CRIAR_COBRANCA', f'Cobrança #{cobranca.pk} criada para {aluno.nome_completo}')
    return cobranca


@transaction.atomic
def gerar_cobrancas_turma(turma, plano: PlanoFinanceiro, vencimento: date, criado_por) -> int:
    from apps.aluno.models import MatriculaTurma
    from apps.ano_letivo.models import AnoLetivo

    ano_ativo = AnoLetivo.objects.filter(escola=turma.escola, ativo=True).first()
    matriculas = MatriculaTurma.objects.filter(
        turma=turma,
        ano_letivo=ano_ativo,
        ativo=True,
    ).select_related('aluno')

    count = 0
    for mat in matriculas:
        gerar_cobranca_aluno(
            aluno=mat.aluno,
            dados={
                'plano_financeiro': plano,
                'descricao': plano.nome,
                'valor': plano.valor,
                'vencimento': vencimento,
                'gateway': GatewayCobranca.MANUAL,
            },
            criado_por=criado_por,
        )
        count += 1
    return count


@transaction.atomic
def gerar_cobrancas_escola(escola, plano: PlanoFinanceiro, vencimento: date, criado_por) -> int:
    from apps.aluno.models import MatriculaTurma
    from apps.ano_letivo.models import AnoLetivo

    ano_ativo = AnoLetivo.objects.filter(escola=escola, ativo=True).first()
    matriculas = MatriculaTurma.objects.filter(
        turma__escola=escola,
        ano_letivo=ano_ativo,
        ativo=True,
    ).select_related('aluno').distinct()

    count = 0
    for mat in matriculas:
        gerar_cobranca_aluno(
            aluno=mat.aluno,
            dados={
                'plano_financeiro': plano,
                'descricao': plano.nome,
                'valor': plano.valor,
                'vencimento': vencimento,
                'gateway': GatewayCobranca.MANUAL,
            },
            criado_por=criado_por,
        )
        count += 1
    return count


@transaction.atomic
def registrar_pagamento_manual(cobranca: CobrancaAluno, usuario) -> CobrancaAluno:
    if cobranca.status in (StatusCobranca.PAGO, StatusCobranca.CANCELADO):
        raise ValueError(f'Cobrança já está {cobranca.get_status_display()}.')
    cobranca.status  = StatusCobranca.PAGO
    cobranca.pago_em = timezone.now()
    cobranca.save(update_fields=['status', 'pago_em'])
    _registrar_auditoria(usuario, 'PAGAMENTO_MANUAL', f'Cobrança #{cobranca.pk} marcada como paga manualmente')
    return cobranca


@transaction.atomic
def cancelar(cobranca: CobrancaAluno, usuario) -> CobrancaAluno:
    if cobranca.status == StatusCobranca.CANCELADO:
        raise ValueError('Cobrança já está cancelada.')
    cobranca.status = StatusCobranca.CANCELADO
    cobranca.save(update_fields=['status'])
    _registrar_auditoria(usuario, 'CANCELAR_COBRANCA', f'Cobrança #{cobranca.pk} cancelada')
    return cobranca


def processar_webhook(gateway: str, payload: dict):
    """Stub — recebe payload do gateway e atualiza status via gateway_id."""
    gateway_id = payload.get('id') or payload.get('gateway_id', '')
    if not gateway_id:
        logger.warning('processar_webhook: payload sem gateway_id — %s', payload)
        return

    try:
        cobranca = CobrancaAluno.objects.get(gateway=gateway, gateway_id=str(gateway_id))
    except CobrancaAluno.DoesNotExist:
        logger.warning('processar_webhook: cobrança não encontrada para gateway_id=%s', gateway_id)
        return

    status_map = {
        'approved': StatusCobranca.PAGO,
        'pending':  StatusCobranca.PENDENTE,
        'rejected': StatusCobranca.CANCELADO,
    }
    novo_status = status_map.get(payload.get('status', ''))
    if novo_status and cobranca.status != novo_status:
        cobranca.status = novo_status
        if novo_status == StatusCobranca.PAGO:
            cobranca.pago_em = timezone.now()
        cobranca.save(update_fields=['status', 'pago_em'] if novo_status == StatusCobranca.PAGO else ['status'])
        logger.info('processar_webhook: cobrança #%s → %s', cobranca.pk, novo_status)


def verificar_vencimentos():
    """Transiciona cobranças PENDENTE vencidas → VENCIDO, respeitando dias_tolerancia."""
    hoje = date.today()
    pendentes = CobrancaAluno.objects.filter(status=StatusCobranca.PENDENTE).select_related('aluno__escola')

    por_escola: dict[int, int] = {}
    for c in pendentes:
        escola_id = _escola_da_cobranca(c)
        if escola_id not in por_escola:
            por_escola[escola_id] = _dias_tolerancia(escola_id)

    atualizadas = 0
    for c in pendentes:
        escola_id   = _escola_da_cobranca(c)
        tolerancia  = por_escola.get(escola_id, 3)
        from datetime import timedelta
        if c.vencimento + timedelta(days=tolerancia) < hoje:
            c.status = StatusCobranca.VENCIDO
            c.save(update_fields=['status'])
            _notificar_vencimento(c)
            atualizadas += 1

    logger.info('verificar_vencimentos: %d cobranças marcadas como VENCIDO', atualizadas)
    return atualizadas


def _escola_da_cobranca(cobranca: CobrancaAluno) -> int:
    try:
        return cobranca.aluno.escola_id
    except Exception:
        return 0


def _dias_tolerancia(escola_id: int) -> int:
    try:
        from apps.configuracao.models import ConfiguracaoFinanceira
        cfg = ConfiguracaoFinanceira.objects.get(escola_id=escola_id)
        return cfg.dias_tolerancia
    except Exception:
        return 3


def _notificar_vencimento(cobranca: CobrancaAluno):
    try:
        from apps.notificacao.services import notificacao_service
        notificacao_service.criar(
            escola_id=_escola_da_cobranca(cobranca),
            titulo='Cobrança vencida',
            mensagem=f'A cobrança "{cobranca.descricao}" do aluno {cobranca.aluno.nome_completo} está vencida.',
            tipo='FINANCEIRO',
        )
    except Exception:
        pass


def _registrar_auditoria(usuario, acao: str, detalhe: str):
    try:
        from apps.auditoria.services import auditoria_service
        auditoria_service.registrar(usuario=usuario, acao=acao, detalhe=detalhe)
    except Exception:
        pass
