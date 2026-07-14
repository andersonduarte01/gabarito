from django.db import models


class StatusAnoLetivo(models.TextChoices):
    EM_PLANEJAMENTO = 'EM_PLANEJAMENTO', 'Em Planejamento'
    EM_ANDAMENTO    = 'EM_ANDAMENTO',    'Em Andamento'
    ENCERRADO       = 'ENCERRADO',       'Encerrado'


class TipoPeriodo(models.TextChoices):
    LETIVO  = 'LETIVO',  'Letivo'
    RECESSO = 'RECESSO', 'Recesso / Férias'


class AnoLetivo(models.Model):
    escola      = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='anos_letivos',
        verbose_name='Escola',
    )
    ano         = models.PositiveSmallIntegerField('Ano')
    data_inicio = models.DateField('Data de Início')
    data_fim    = models.DateField('Data de Fim')
    status      = models.CharField(
        'Status',
        max_length=20,
        choices=StatusAnoLetivo.choices,
        default=StatusAnoLetivo.EM_PLANEJAMENTO,
    )
    criado_por  = models.ForeignKey(
        'core.Usuario',
        null=True,
        on_delete=models.SET_NULL,
        related_name='anos_letivos_criados',
        verbose_name='Criado por',
    )
    criado_em     = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'
        ordering            = ['-ano']
        unique_together     = (('escola', 'ano'),)

    def __str__(self):
        return f'{self.ano} — {self.escola} ({self.get_status_display()})'

    @property
    def em_planejamento(self):
        return self.status == StatusAnoLetivo.EM_PLANEJAMENTO

    @property
    def em_andamento(self):
        return self.status == StatusAnoLetivo.EM_ANDAMENTO

    @property
    def encerrado(self):
        return self.status == StatusAnoLetivo.ENCERRADO


class PeriodoLetivo(models.Model):
    ano_letivo  = models.ForeignKey(
        AnoLetivo,
        on_delete=models.CASCADE,
        related_name='periodos',
        verbose_name='Ano Letivo',
    )
    numero      = models.PositiveSmallIntegerField('Número')
    nome        = models.CharField('Nome', max_length=50)
    tipo        = models.CharField(
        'Tipo',
        max_length=10,
        choices=TipoPeriodo.choices,
        default=TipoPeriodo.LETIVO,
    )
    data_inicio = models.DateField('Data de Início')
    data_fim    = models.DateField('Data de Fim')

    class Meta:
        verbose_name        = 'Período Letivo'
        verbose_name_plural = 'Períodos Letivos'
        ordering            = ['numero']
        unique_together     = (('ano_letivo', 'numero'),)

    def __str__(self):
        return f'{self.nome} — {self.ano_letivo.ano}'

    @property
    def is_recesso(self):
        return self.tipo == TipoPeriodo.RECESSO
