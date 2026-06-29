from decimal import Decimal

from django.db import transaction


# ---------------------------------------------------------------------------
# criar_registro
# ---------------------------------------------------------------------------

@transaction.atomic
def criar_registro(turma, materia, professor, data, ano_letivo, periodo_letivo=None, criado_por=None):
    from apps.frequencia.models import RegistroFrequencia
    return RegistroFrequencia.objects.create(
        turma=turma,
        materia=materia,
        professor=professor,
        data=data,
        ano_letivo=ano_letivo,
        periodo_letivo=periodo_letivo,
        criado_por=criado_por,
    )


# ---------------------------------------------------------------------------
# lancar_presencas
# ---------------------------------------------------------------------------

@transaction.atomic
def lancar_presencas(registro, entradas: list) -> int:
    """
    entradas: [{'aluno_id': pk, 'presente': bool, 'justificado': bool, 'observacao': str}]
    Salva/atualiza PresencaAluno e dispara verificação de alertas.
    Returns count of records saved.
    """
    from apps.frequencia.models import PresencaAluno
    from apps.aluno.models import Aluno

    alunos = {a.pk: a for a in Aluno.objects.filter(pk__in=[e['aluno_id'] for e in entradas])}
    count = 0
    alunos_afetados = []

    for entrada in entradas:
        aluno = alunos.get(entrada['aluno_id'])
        if aluno is None:
            continue
        presente    = bool(entrada.get('presente', True))
        justificado = bool(entrada.get('justificado', False)) and not presente
        observacao  = entrada.get('observacao', '')

        PresencaAluno.objects.update_or_create(
            registro=registro,
            aluno=aluno,
            defaults={
                'presente':    presente,
                'justificado': justificado,
                'observacao':  observacao,
            },
        )
        count += 1
        alunos_afetados.append(aluno)

    # Dispara alertas e atualiza boletim para cada aluno afetado
    if registro.periodo_letivo and registro.materia:
        for aluno in alunos_afetados:
            verificar_alertas(aluno, registro.materia, registro.periodo_letivo)
            _atualizar_boletim(aluno, registro.materia, registro.periodo_letivo)

    return count


# ---------------------------------------------------------------------------
# justificar_falta
# ---------------------------------------------------------------------------

@transaction.atomic
def justificar_falta(presenca, observacao: str = '') -> None:
    presenca.justificado = True
    presenca.observacao  = observacao
    presenca.save(update_fields=['justificado', 'observacao'])
    # Recalcula boletim se tiver matéria+período
    registro = presenca.registro
    if registro.periodo_letivo and registro.materia:
        _atualizar_boletim(presenca.aluno, registro.materia, registro.periodo_letivo)


# ---------------------------------------------------------------------------
# cancelar_aula
# ---------------------------------------------------------------------------

@transaction.atomic
def cancelar_aula(registro) -> None:
    registro.delete()


# ---------------------------------------------------------------------------
# calcular_percentual
# ---------------------------------------------------------------------------

def calcular_percentual(aluno, materia, periodo_letivo) -> Decimal:
    """
    Returns frequência percentual for aluno/materia/period.
    Counts total aulas (RegistroFrequencia) and presencas (PresencaAluno.presente=True).
    """
    from apps.frequencia.models import RegistroFrequencia, PresencaAluno
    from apps.aluno.models import MatriculaTurma

    matricula = (
        MatriculaTurma.objects
        .filter(aluno=aluno, ano_letivo=periodo_letivo.ano_letivo, ativo=True)
        .first()
    )
    if not matricula:
        return Decimal('100.00')

    registros = RegistroFrequencia.objects.filter(
        turma=matricula.turma,
        materia=materia,
        periodo_letivo=periodo_letivo,
    )
    total = registros.count()
    if not total:
        return Decimal('100.00')

    presentes = PresencaAluno.objects.filter(
        registro__in=registros,
        aluno=aluno,
        presente=True,
    ).count()

    return (Decimal(presentes) / Decimal(total) * 100).quantize(Decimal('0.01'))


# ---------------------------------------------------------------------------
# verificar_alertas
# ---------------------------------------------------------------------------

def verificar_alertas(aluno, materia, periodo_letivo) -> None:
    """Sends notifications if frequency drops below alert thresholds."""
    from apps.configuracao.models import ConfiguracaoFrequencia
    from apps.notificacao.models import TipoNotificacao
    from apps.notificacao.services import notificacao_service

    ano_letivo = periodo_letivo.ano_letivo
    try:
        config = ConfiguracaoFrequencia.objects.get(escola=ano_letivo.escola)
        limite_min    = config.percentual_minimo_frequencia
        limite_alerta = config.percentual_alerta_prevencao
    except ConfiguracaoFrequencia.DoesNotExist:
        limite_min    = Decimal('75.00')
        limite_alerta = Decimal('80.00')

    percentual = calcular_percentual(aluno, materia, periodo_letivo)

    if percentual < limite_min:
        titulo   = f'⚠️ Frequência crítica — {aluno.nome_completo}'
        mensagem = (
            f'{aluno.nome_completo} está com {percentual}% de frequência em '
            f'{materia.nome} ({periodo_letivo.nome}). '
            f'Mínimo exigido: {limite_min}%.'
        )
        _notificar_diretores(ano_letivo.escola, titulo, mensagem, TipoNotificacao.ACADEMICA)
        _notificar_responsaveis(aluno, titulo, mensagem, TipoNotificacao.ACADEMICA)

    elif percentual < limite_alerta:
        titulo   = f'Alerta de frequência — {aluno.nome_completo}'
        mensagem = (
            f'{aluno.nome_completo} está com {percentual}% de frequência em '
            f'{materia.nome} ({periodo_letivo.nome}). '
            f'Atenção: mínimo exigido é {limite_min}%.'
        )
        _notificar_diretores(ano_letivo.escola, titulo, mensagem, TipoNotificacao.ACADEMICA)
        _notificar_responsaveis(aluno, titulo, mensagem, TipoNotificacao.ACADEMICA)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _notificar_diretores(escola, titulo, mensagem, tipo):
    from apps.notificacao.services import notificacao_service
    from apps.core.models import PapelVinculo
    papeis = (
        PapelVinculo.objects
        .filter(vinculo__escola=escola, tipo='DIRETOR', ativo=True)
        .select_related('vinculo__usuario')
    )
    for papel in papeis:
        notificacao_service.criar(papel.vinculo.usuario, titulo, mensagem, tipo)


def _notificar_responsaveis(aluno, titulo, mensagem, tipo):
    from apps.notificacao.services import notificacao_service
    from apps.responsavel.models import VinculoResponsavelAluno
    vinculos = (
        VinculoResponsavelAluno.objects
        .filter(aluno=aluno, ativo=True)
        .select_related('responsavel__usuario')
    )
    for v in vinculos:
        if v.responsavel.usuario:
            notificacao_service.criar(v.responsavel.usuario, titulo, mensagem, tipo)


def _atualizar_boletim(aluno, materia, periodo_letivo):
    """Re-runs calcular_periodo so the boletim reflects updated frequency."""
    try:
        from apps.boletim.services import boletim_service
        boletim_service.calcular_periodo(aluno, materia, periodo_letivo)
    except Exception:
        pass
