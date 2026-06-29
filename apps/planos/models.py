from datetime import date

from django.db import models

from apps.core.modulos import CodigoModulo


class StatusAssinatura(models.TextChoices):
    TRIAL          = 'TRIAL',          'Trial'
    TRIAL_EXPIRADO = 'TRIAL_EXPIRADO', 'Trial Expirado'
    ATIVA          = 'ATIVA',          'Ativa'
    GRACE          = 'GRACE',          'Carência'
    SUSPENSA       = 'SUSPENSA',       'Suspensa'
    CANCELADA      = 'CANCELADA',      'Cancelada'


# Status que permitem acesso total ao sistema
STATUS_COM_ACESSO = frozenset({
    StatusAssinatura.TRIAL,
    StatusAssinatura.ATIVA,
    StatusAssinatura.GRACE,
})


class Modulo(models.Model):
    codigo           = models.CharField('Código', max_length=50, unique=True)
    nome             = models.CharField('Nome', max_length=100)
    ativo_plataforma = models.BooleanField('Ativo na Plataforma', default=True)

    class Meta:
        verbose_name        = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering            = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.codigo})'


class Plano(models.Model):
    nome         = models.CharField('Nome', max_length=100, unique=True)
    descricao    = models.TextField('Descrição', blank=True)
    preco_mensal = models.DecimalField('Preço Mensal (R$)', max_digits=8, decimal_places=2)
    modulos      = models.ManyToManyField(
        Modulo,
        verbose_name='Módulos incluídos',
        blank=True,
    )
    ativo        = models.BooleanField('Ativo para venda', default=True)

    class Meta:
        verbose_name        = 'Plano'
        verbose_name_plural = 'Planos'
        ordering            = ['preco_mensal']

    def __str__(self):
        return self.nome


class AssinaturaEscola(models.Model):
    escola               = models.OneToOneField(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='assinatura',
        verbose_name='Escola',
    )
    plano                = models.ForeignKey(
        Plano,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='assinaturas',
        verbose_name='Plano',
    )
    status               = models.CharField(
        'Status',
        max_length=20,
        choices=StatusAssinatura.choices,
        default=StatusAssinatura.TRIAL,
    )

    # --- Trial ---
    data_inicio_trial    = models.DateField('Início do Trial', null=True, blank=True)
    limite_alunos_trial  = models.PositiveIntegerField('Limite de alunos (trial)', default=30)
    duracao_trial_dias   = models.PositiveIntegerField('Duração do trial (dias)', default=10)

    # --- Assinatura ativa ---
    data_inicio          = models.DateField('Data de início', null=True, blank=True)
    data_vencimento      = models.DateField('Data de vencimento', null=True, blank=True)

    # --- Grace period ---
    data_grace_fim       = models.DateField('Fim da carência', null=True, blank=True)

    # --- Auditoria ---
    ativado_por          = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assinaturas_ativadas',
        verbose_name='Ativado por',
    )
    atualizado_em        = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Assinatura da Escola'
        verbose_name_plural = 'Assinaturas das Escolas'

    def __str__(self):
        return f'{self.escola} — {self.get_status_display()}'

    @property
    def acesso_permitido(self) -> bool:
        return self.status in STATUS_COM_ACESSO

    def trial_valido(self) -> bool:
        from datetime import timedelta
        if not self.data_inicio_trial:
            return False
        prazo = self.data_inicio_trial + timedelta(days=self.duracao_trial_dias)
        return date.today() <= prazo

    def dias_restantes_grace(self) -> int | None:
        if self.status != StatusAssinatura.GRACE or not self.data_grace_fim:
            return None
        delta = self.data_grace_fim - date.today()
        return max(0, delta.days)


class ModuloEscola(models.Model):
    assinatura = models.ForeignKey(
        AssinaturaEscola,
        on_delete=models.CASCADE,
        related_name='modulos_escola',
        verbose_name='Assinatura',
    )
    modulo     = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name='modulos_escola',
        verbose_name='Módulo',
    )
    ativo      = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Módulo da Escola'
        verbose_name_plural = 'Módulos da Escola'
        unique_together     = ('assinatura', 'modulo')

    def __str__(self):
        return f'{self.assinatura.escola} — {self.modulo.nome}'


class HistoricoAssinatura(models.Model):
    assinatura      = models.ForeignKey(
        AssinaturaEscola,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name='Assinatura',
    )
    status_anterior = models.CharField('Status anterior', max_length=20, choices=StatusAssinatura.choices)
    status_novo     = models.CharField('Status novo', max_length=20, choices=StatusAssinatura.choices)
    plano_anterior  = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='historico_como_anterior',
        verbose_name='Plano anterior',
    )
    plano_novo      = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='historico_como_novo',
        verbose_name='Plano novo',
    )
    alterado_por    = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alteracoes_assinatura',
        verbose_name='Alterado por',
    )
    alterado_em     = models.DateTimeField('Alterado em', auto_now_add=True)
    observacao      = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name        = 'Histórico de Assinatura'
        verbose_name_plural = 'Histórico de Assinaturas'
        ordering            = ['-alterado_em']

    def __str__(self):
        return f'{self.assinatura.escola}: {self.status_anterior} → {self.status_novo}'
