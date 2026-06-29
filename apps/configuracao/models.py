from django.db import models


class TipoPeriodoLetivo(models.TextChoices):
    BIMESTRAL  = 'BIMESTRAL',  'Bimestral'
    TRIMESTRAL = 'TRIMESTRAL', 'Trimestral'
    SEMESTRAL  = 'SEMESTRAL',  'Semestral'


class TipoCalculoMedia(models.TextChoices):
    SIMPLES   = 'SIMPLES',   'Simples'
    PONDERADA = 'PONDERADA', 'Ponderada'


class ModoLancamentoFrequencia(models.TextChoices):
    DIARIO  = 'DIARIO',  'Diário'
    SEMANAL = 'SEMANAL', 'Semanal'
    MENSAL  = 'MENSAL',  'Mensal'


class ConfiguracaoAcademica(models.Model):
    escola                   = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='configuracao_academica',
        verbose_name='Escola',
    )
    nota_maxima              = models.DecimalField(
        'Nota máxima',
        max_digits=5,
        decimal_places=2,
        default=10.0,
    )
    nota_minima_aprovacao    = models.DecimalField(
        'Nota mínima para aprovação',
        max_digits=5,
        decimal_places=2,
        default=5.0,
    )
    tipo_periodo_letivo      = models.CharField(
        'Tipo de Período Letivo',
        max_length=15,
        choices=TipoPeriodoLetivo.choices,
        default=TipoPeriodoLetivo.BIMESTRAL,
    )
    casas_decimais_nota      = models.PositiveSmallIntegerField(
        'Casas decimais na nota',
        default=1,
        help_text='0, 1 ou 2 casas decimais.',
    )
    tipo_calculo_media       = models.CharField(
        'Tipo de Cálculo de Média',
        max_length=10,
        choices=TipoCalculoMedia.choices,
        default=TipoCalculoMedia.SIMPLES,
    )
    exige_recuperacao        = models.BooleanField('Exige Recuperação', default=True)
    nota_minima_recuperacao  = models.DecimalField(
        'Nota mínima para ir à recuperação',
        max_digits=5,
        decimal_places=2,
        default=3.0,
    )

    class Meta:
        verbose_name        = 'Configuração Acadêmica'
        verbose_name_plural = 'Configurações Acadêmicas'

    def __str__(self):
        return f'Acadêmico — {self.escola}'


class ConfiguracaoFrequencia(models.Model):
    escola                      = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='configuracao_frequencia',
        verbose_name='Escola',
    )
    percentual_minimo_frequencia = models.DecimalField(
        'Percentual mínimo de frequência (%)',
        max_digits=5,
        decimal_places=2,
        default=75.0,
        help_text='Exigência legal brasileira mínima: 75%.',
    )
    percentual_alerta_prevencao  = models.DecimalField(
        'Percentual de alerta preventivo (%)',
        max_digits=5,
        decimal_places=2,
        default=80.0,
        help_text='Notificação enviada antes de atingir o mínimo legal.',
    )
    modo_lancamento              = models.CharField(
        'Modo de Lançamento',
        max_length=10,
        choices=ModoLancamentoFrequencia.choices,
        default=ModoLancamentoFrequencia.DIARIO,
    )

    class Meta:
        verbose_name        = 'Configuração de Frequência'
        verbose_name_plural = 'Configurações de Frequência'

    def __str__(self):
        return f'Frequência — {self.escola}'


class GatewayPadrao(models.TextChoices):
    MERCADO_PAGO = 'MERCADO_PAGO', 'Mercado Pago'
    MANUAL       = 'MANUAL',       'Manual (físico)'


class ConfiguracaoFinanceira(models.Model):
    escola                = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='configuracao_financeira',
        verbose_name='Escola',
    )
    multa_percentual      = models.DecimalField(
        'Multa por atraso (%)', max_digits=5, decimal_places=2, default=2.0,
    )
    juros_percentual_mes  = models.DecimalField(
        'Juros ao mês (%)', max_digits=5, decimal_places=2, default=1.0,
    )
    dias_tolerancia       = models.PositiveSmallIntegerField(
        'Dias de tolerância',
        default=3,
        help_text='Dias após o vencimento antes de marcar como VENCIDO.',
    )
    gateway_padrao        = models.CharField(
        'Gateway padrão', max_length=20,
        choices=GatewayPadrao.choices,
        default=GatewayPadrao.MANUAL,
    )

    class Meta:
        verbose_name        = 'Configuração Financeira'
        verbose_name_plural = 'Configurações Financeiras'

    def __str__(self):
        return f'Financeiro — {self.escola}'


class ConfiguracaoProfessor(models.Model):
    escola                       = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='configuracao_professor',
        verbose_name='Escola',
    )
    carga_horaria_maxima_semanal = models.PositiveSmallIntegerField(
        'Carga horária máxima semanal (horas)',
        default=40,
        help_text='Teto de alerta — não bloqueia a criação de aulas.',
    )

    class Meta:
        verbose_name        = 'Configuração de Professor'
        verbose_name_plural = 'Configurações de Professor'

    def __str__(self):
        return f'Professor — {self.escola}'
