from decimal import Decimal

from django.db import transaction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_config(escola):
    from apps.configuracao.models import ConfiguracaoAcademica
    try:
        return ConfiguracaoAcademica.objects.get(escola=escola)
    except ConfiguracaoAcademica.DoesNotExist:
        return None


def _media(notas_qs, tipo_calculo):
    """Weighted or simple average from a NotaAluno queryset."""
    notas = list(notas_qs.select_related('avaliacao'))
    if not notas:
        return None
    if tipo_calculo == 'PONDERADA':
        total_peso = sum(n.avaliacao.peso for n in notas)
        if not total_peso:
            return Decimal('0')
        return sum(n.nota * n.avaliacao.peso for n in notas) / total_peso
    total = sum(n.nota for n in notas)
    return total / len(notas)


# ---------------------------------------------------------------------------
# calcular_periodo
# ---------------------------------------------------------------------------

@transaction.atomic
def calcular_periodo(aluno, materia, periodo_letivo):
    """
    Recalculates ResultadoPeriodo for one aluno/materia/period.
    Called automatically after note entry if the avaliação has a periodo_letivo.
    """
    from apps.avaliacao.models import Avaliacao, NotaAluno
    from apps.aluno.models import MatriculaTurma
    from apps.boletim.models import ResultadoPeriodo, SituacaoPeriodo

    ano_letivo = periodo_letivo.ano_letivo

    matricula = (
        MatriculaTurma.objects
        .filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True)
        .select_related('turma__escola')
        .first()
    )
    if not matricula:
        return None

    escola = matricula.turma.escola
    config = _get_config(escola)
    nota_minima      = config.nota_minima_aprovacao     if config else Decimal('5.0')
    nota_minima_rec  = config.nota_minima_recuperacao   if config else Decimal('3.0')
    exige_rec        = config.exige_recuperacao         if config else True
    tipo_calculo     = config.tipo_calculo_media        if config else 'SIMPLES'

    from apps.configuracao.models import ConfiguracaoFrequencia
    try:
        cfg_freq = ConfiguracaoFrequencia.objects.get(escola=escola)
        freq_minima = cfg_freq.percentual_minimo_frequencia
    except ConfiguracaoFrequencia.DoesNotExist:
        freq_minima = Decimal('75.0')

    avaliacoes = Avaliacao.objects.filter(
        turma=matricula.turma,
        materia=materia,
        periodo_letivo=periodo_letivo,
    )
    notas_qs = (
        NotaAluno.objects
        .filter(avaliacao__in=avaliacoes, aluno=aluno, ausente=False)
        .exclude(nota__isnull=True)
    )

    media = _media(notas_qs, tipo_calculo)

    # Get real frequency (M18 — falls back to 100% when no registros exist)
    try:
        from apps.frequencia.services import frequencia_service
        frequencia_calc = frequencia_service.calcular_percentual(aluno, materia, periodo_letivo)
    except Exception:
        frequencia_calc = Decimal('100.00')

    freq_reprovado = frequencia_calc < freq_minima

    if media is None:
        situacao = SituacaoPeriodo.EM_CURSO
    elif freq_reprovado:
        situacao = SituacaoPeriodo.REPROVADO
    elif media >= nota_minima:
        situacao = SituacaoPeriodo.APROVADO
    elif exige_rec and media >= nota_minima_rec:
        situacao = SituacaoPeriodo.RECUPERACAO
    else:
        situacao = SituacaoPeriodo.REPROVADO

    resultado, _ = ResultadoPeriodo.objects.update_or_create(
        aluno=aluno, materia=materia, periodo_letivo=periodo_letivo,
        defaults={
            'ano_letivo':             ano_letivo,
            'media_periodo':          media,
            'frequencia_percentual':  frequencia_calc,
            'situacao_periodo':       situacao,
        },
    )
    return resultado


# ---------------------------------------------------------------------------
# calcular_periodo_turma  (batch for a whole turma)
# ---------------------------------------------------------------------------

@transaction.atomic
def calcular_periodo_turma(turma, periodo_letivo):
    """Recalculates ResultadoPeriodo for every active aluno in the turma."""
    from apps.aluno.models import MatriculaTurma
    from apps.materia.models import Materia

    matriculas = (
        MatriculaTurma.objects
        .filter(turma=turma, ano_letivo=periodo_letivo.ano_letivo, ativo=True)
        .select_related('aluno')
    )
    materias = Materia.objects.filter(escola=turma.escola, ativo=True)

    count = 0
    for mat in matriculas:
        for materia in materias:
            calcular_periodo(mat.aluno, materia, periodo_letivo)
            count += 1
    return count


# ---------------------------------------------------------------------------
# calcular_ano
# ---------------------------------------------------------------------------

@transaction.atomic
def calcular_ano(aluno, materia, ano_letivo):
    """Consolidates all periods into a ResultadoAnual."""
    from apps.boletim.models import ResultadoPeriodo, ResultadoAnual, SituacaoFinal

    escola = ano_letivo.escola
    config = _get_config(escola)
    nota_minima       = config.nota_minima_aprovacao       if config else Decimal('5.0')
    percentual_minimo = Decimal('75.0')  # M18 not implemented

    periodos = list(
        ResultadoPeriodo.objects
        .filter(aluno=aluno, materia=materia, ano_letivo=ano_letivo)
        .exclude(media_periodo__isnull=True)
    )
    if not periodos:
        return None

    media_anual  = sum(p.media_periodo for p in periodos) / len(periodos)
    freq_anual   = sum(p.frequencia_percentual for p in periodos) / len(periodos)

    if media_anual >= nota_minima and freq_anual >= percentual_minimo:
        situacao = SituacaoFinal.APROVADO
    else:
        situacao = SituacaoFinal.REPROVADO

    resultado, _ = ResultadoAnual.objects.update_or_create(
        aluno=aluno, materia=materia, ano_letivo=ano_letivo,
        defaults={
            'media_anual':      media_anual,
            'frequencia_anual': freq_anual,
            'situacao_final':   situacao,
        },
    )
    return resultado


# ---------------------------------------------------------------------------
# calcular_ano_turma  (batch)
# ---------------------------------------------------------------------------

@transaction.atomic
def calcular_ano_turma(turma, ano_letivo):
    """Calculates ResultadoAnual for every active aluno in the turma."""
    from apps.aluno.models import MatriculaTurma
    from apps.materia.models import Materia

    matriculas = (
        MatriculaTurma.objects
        .filter(turma=turma, ano_letivo=ano_letivo, ativo=True)
        .select_related('aluno')
    )
    materias = Materia.objects.filter(escola=turma.escola, ativo=True)

    count = 0
    for mat in matriculas:
        for materia in materias:
            calcular_ano(mat.aluno, materia, ano_letivo)
            count += 1
    return count


# ---------------------------------------------------------------------------
# aprovar_conselho
# ---------------------------------------------------------------------------

@transaction.atomic
def aprovar_conselho(resultado_anual, request=None):
    from apps.boletim.models import SituacaoFinal
    resultado_anual.situacao_final = SituacaoFinal.APROVADO_CONSELHO
    resultado_anual.save(update_fields=['situacao_final', 'calculado_em'])
    if request:
        from apps.auditoria.services import auditoria_service
        from apps.auditoria.models import AcaoAuditoria
        auditoria_service.registrar(
            request=request,
            acao=AcaoAuditoria.EDITAR,
            objeto=resultado_anual,
            descricao=f'Aprovação por conselho de classe: {resultado_anual.aluno.nome_completo} | {resultado_anual.materia.nome}',
        )
    return resultado_anual
