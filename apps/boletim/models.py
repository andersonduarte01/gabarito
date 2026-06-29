from decimal import Decimal

from django.db import models


class SituacaoPeriodo(models.TextChoices):
    EM_CURSO    = 'EM_CURSO',    'Em Curso'
    APROVADO    = 'APROVADO',    'Aprovado'
    RECUPERACAO = 'RECUPERACAO', 'Em Recuperação'
    REPROVADO   = 'REPROVADO',   'Reprovado'


class SituacaoFinal(models.TextChoices):
    APROVADO          = 'APROVADO',          'Aprovado'
    REPROVADO         = 'REPROVADO',         'Reprovado'
    APROVADO_CONSELHO = 'APROVADO_CONSELHO', 'Aprovado pelo Conselho'


class ResultadoPeriodo(models.Model):
    aluno              = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='resultados_periodo', verbose_name='Aluno',
    )
    materia            = models.ForeignKey(
        'materia.Materia', on_delete=models.CASCADE,
        related_name='resultados_periodo', verbose_name='Matéria',
    )
    periodo_letivo     = models.ForeignKey(
        'ano_letivo.PeriodoLetivo', on_delete=models.CASCADE,
        related_name='resultados', verbose_name='Período Letivo',
    )
    ano_letivo         = models.ForeignKey(
        'ano_letivo.AnoLetivo', on_delete=models.CASCADE,
        related_name='resultados_periodo', verbose_name='Ano Letivo',
    )
    media_periodo      = models.DecimalField(
        'Média do Período', max_digits=5, decimal_places=2,
        null=True, blank=True,
    )
    frequencia_percentual = models.DecimalField(
        'Frequência (%)', max_digits=5, decimal_places=2,
        default=Decimal('100.00'),
    )
    situacao_periodo   = models.CharField(
        'Situação', max_length=20,
        choices=SituacaoPeriodo.choices,
        default=SituacaoPeriodo.EM_CURSO,
    )
    calculado_em       = models.DateTimeField('Calculado em', auto_now=True)

    class Meta:
        verbose_name        = 'Resultado do Período'
        verbose_name_plural = 'Resultados dos Períodos'
        unique_together     = ('aluno', 'materia', 'periodo_letivo')
        ordering            = ['periodo_letivo__numero', 'materia__nome']

    def __str__(self):
        return f'{self.aluno.nome_completo} | {self.materia.nome} | {self.periodo_letivo.nome}'


class ResultadoAnual(models.Model):
    aluno              = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='resultados_anuais', verbose_name='Aluno',
    )
    materia            = models.ForeignKey(
        'materia.Materia', on_delete=models.CASCADE,
        related_name='resultados_anuais', verbose_name='Matéria',
    )
    ano_letivo         = models.ForeignKey(
        'ano_letivo.AnoLetivo', on_delete=models.CASCADE,
        related_name='resultados_anuais', verbose_name='Ano Letivo',
    )
    media_anual        = models.DecimalField(
        'Média Anual', max_digits=5, decimal_places=2,
        null=True, blank=True,
    )
    frequencia_anual   = models.DecimalField(
        'Frequência Anual (%)', max_digits=5, decimal_places=2,
        default=Decimal('100.00'),
    )
    situacao_final     = models.CharField(
        'Situação Final', max_length=20,
        choices=SituacaoFinal.choices,
        default=SituacaoFinal.REPROVADO,
    )
    calculado_em       = models.DateTimeField('Calculado em', auto_now=True)

    class Meta:
        verbose_name        = 'Resultado Anual'
        verbose_name_plural = 'Resultados Anuais'
        unique_together     = ('aluno', 'materia', 'ano_letivo')
        ordering            = ['materia__nome']

    def __str__(self):
        return f'{self.aluno.nome_completo} | {self.materia.nome} | {self.ano_letivo.ano}'
