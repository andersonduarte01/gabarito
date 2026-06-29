from django.db import models


class Periodicidade(models.TextChoices):
    MENSAL = 'MENSAL', 'Mensal'
    ANUAL  = 'ANUAL',  'Anual'
    AVULSO = 'AVULSO', 'Avulso'


class StatusCobranca(models.TextChoices):
    PENDENTE  = 'PENDENTE',  'Pendente'
    PAGO      = 'PAGO',      'Pago'
    VENCIDO   = 'VENCIDO',   'Vencido'
    CANCELADO = 'CANCELADO', 'Cancelado'


class GatewayCobranca(models.TextChoices):
    MERCADO_PAGO = 'MERCADO_PAGO', 'Mercado Pago'
    MANUAL       = 'MANUAL',       'Manual (físico)'


class PlanoFinanceiro(models.Model):
    escola        = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='planos_financeiros',
        verbose_name='Escola',
    )
    nome          = models.CharField('Nome', max_length=120)
    descricao     = models.TextField('Descrição', blank=True)
    valor         = models.DecimalField('Valor (R$)', max_digits=10, decimal_places=2)
    periodicidade = models.CharField(
        'Periodicidade', max_length=10,
        choices=Periodicidade.choices, default=Periodicidade.MENSAL,
    )
    ativo         = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Plano Financeiro'
        verbose_name_plural = 'Planos Financeiros'
        ordering            = ['nome']

    def __str__(self):
        return f'{self.nome} — R$ {self.valor}'


class CobrancaAluno(models.Model):
    aluno                  = models.ForeignKey(
        'aluno.Aluno',
        on_delete=models.CASCADE,
        related_name='cobrancas',
        verbose_name='Aluno',
    )
    responsavel_financeiro = models.ForeignKey(
        'responsavel.PerfilResponsavel',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cobrancas',
        verbose_name='Responsável Financeiro',
    )
    plano_financeiro       = models.ForeignKey(
        PlanoFinanceiro,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cobrancas',
        verbose_name='Plano Financeiro',
    )
    descricao              = models.CharField('Descrição', max_length=200)
    valor                  = models.DecimalField('Valor (R$)', max_digits=10, decimal_places=2)
    vencimento             = models.DateField('Vencimento')
    status                 = models.CharField(
        'Status', max_length=15,
        choices=StatusCobranca.choices, default=StatusCobranca.PENDENTE,
    )
    gateway                = models.CharField(
        'Gateway', max_length=20,
        choices=GatewayCobranca.choices, default=GatewayCobranca.MANUAL,
    )
    gateway_id             = models.CharField(
        'ID no Gateway', max_length=120, blank=True,
        help_text='ID da transação no gateway (vazio para pagamentos manuais).',
    )
    criado_em              = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por             = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cobrancas_criadas',
        verbose_name='Criado por',
    )
    pago_em                = models.DateTimeField('Pago em', null=True, blank=True)

    class Meta:
        verbose_name        = 'Cobrança'
        verbose_name_plural = 'Cobranças'
        ordering            = ['-vencimento', '-criado_em']

    def __str__(self):
        return f'{self.aluno.nome_completo} — {self.descricao} ({self.get_status_display()})'

    @property
    def esta_atrasada(self):
        from django.utils import timezone
        return self.status == StatusCobranca.PENDENTE and self.vencimento < timezone.now().date()
