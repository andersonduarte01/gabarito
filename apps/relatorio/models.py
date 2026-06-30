from django.db import models


class TipoRelatorio(models.TextChoices):
    DESEMPENHO_TURMA      = 'DESEMPENHO_TURMA',      'Desempenho por Turma'
    FREQUENCIA_TURMA      = 'FREQUENCIA_TURMA',      'Frequência por Turma'
    FREQUENCIA_ALUNO      = 'FREQUENCIA_ALUNO',      'Frequência por Aluno'
    ALUNOS_EM_RISCO       = 'ALUNOS_EM_RISCO',       'Alunos em Risco'
    BOLETIM_LOTE          = 'BOLETIM_LOTE',          'Boletim em Lote'
    DESEMPENHO_PROFESSOR  = 'DESEMPENHO_PROFESSOR',  'Desempenho por Professor'
    INADIMPLENCIA         = 'INADIMPLENCIA',         'Inadimplência'
    EXTRATO_FINANCEIRO    = 'EXTRATO_FINANCEIRO',    'Extrato Financeiro'


class PeriodicidadeRelatorio(models.TextChoices):
    MENSAL     = 'MENSAL',     'Mensal'
    POR_PERIODO = 'POR_PERIODO', 'Por Período Letivo'
    ANUAL      = 'ANUAL',      'Anual'


class RelatorioAgendado(models.Model):
    escola        = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='relatorios_agendados',
        verbose_name='Escola',
    )
    tipo          = models.CharField('Tipo', max_length=30, choices=TipoRelatorio.choices)
    periodicidade = models.CharField(
        'Periodicidade', max_length=15,
        choices=PeriodicidadeRelatorio.choices,
        default=PeriodicidadeRelatorio.MENSAL,
    )
    parametros    = models.JSONField('Parâmetros', default=dict, blank=True)
    ativo         = models.BooleanField('Ativo', default=True)
    criado_em     = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Relatório Agendado'
        verbose_name_plural = 'Relatórios Agendados'
        ordering            = ['escola', 'tipo']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.escola.nome}'


class RelatorioGerado(models.Model):
    agendado   = models.ForeignKey(
        RelatorioAgendado,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='geracoes',
        verbose_name='Agendado',
    )
    escola     = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='relatorios_gerados',
        verbose_name='Escola',
    )
    tipo       = models.CharField('Tipo', max_length=30, choices=TipoRelatorio.choices)
    parametros = models.JSONField('Parâmetros', default=dict, blank=True)
    arquivo    = models.FileField(
        'Arquivo',
        upload_to='relatorios/%Y/%m/',
        null=True, blank=True,
    )
    gerado_em  = models.DateTimeField('Gerado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Relatório Gerado'
        verbose_name_plural = 'Relatórios Gerados'
        ordering            = ['-gerado_em']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.escola.nome} — {self.gerado_em.strftime("%d/%m/%Y")}'
