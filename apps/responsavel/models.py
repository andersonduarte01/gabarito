from django.db import models


class Parentesco(models.TextChoices):
    PAI               = 'PAI',               'Pai'
    MAE               = 'MAE',               'Mãe'
    AVO               = 'AVO',               'Avó/Avô'
    TIO               = 'TIO',               'Tio/Tia'
    IRMAO             = 'IRMAO',             'Irmão/Irmã'
    RESPONSAVEL_LEGAL = 'RESPONSAVEL_LEGAL', 'Responsável Legal'
    OUTRO             = 'OUTRO',             'Outro'


class PerfilResponsavel(models.Model):
    escola          = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='responsaveis',
        verbose_name='Escola',
        null=True, blank=True,
    )
    usuario         = models.OneToOneField(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='perfil_responsavel',
        verbose_name='Usuário',
    )
    nome            = models.CharField('Nome', max_length=200)
    cpf             = models.CharField('CPF', max_length=14, blank=True)
    rg              = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    telefone        = models.CharField('Telefone', max_length=20, blank=True)
    foto            = models.ImageField('Foto', upload_to='responsaveis/fotos/', null=True, blank=True)
    endereco        = models.OneToOneField(
        'core.Endereco',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='perfil_responsavel',
        verbose_name='Endereço',
    )
    criado_em       = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em   = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Responsável'
        verbose_name_plural = 'Responsáveis'
        ordering            = ['nome']

    def __str__(self):
        return self.nome

    @property
    def email(self):
        return self.usuario.email if self.usuario else None

    @property
    def tem_acesso(self):
        return self.usuario_id is not None


class VinculoResponsavelAluno(models.Model):
    responsavel            = models.ForeignKey(
        PerfilResponsavel,
        on_delete=models.CASCADE,
        related_name='vinculos_aluno',
        verbose_name='Responsável',
    )
    aluno                  = models.ForeignKey(
        'aluno.Aluno',
        on_delete=models.CASCADE,
        related_name='responsaveis',
        verbose_name='Aluno',
    )
    parentesco             = models.CharField(
        'Parentesco', max_length=20, choices=Parentesco.choices,
    )
    responsavel_financeiro = models.BooleanField('Responsável Financeiro', default=False)
    responsavel_principal  = models.BooleanField('Responsável Principal', default=False)
    ativo                  = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Vínculo Responsável-Aluno'
        verbose_name_plural = 'Vínculos Responsável-Aluno'
        unique_together     = ('responsavel', 'aluno')
        constraints = [
            models.UniqueConstraint(
                fields=['aluno'],
                condition=models.Q(responsavel_principal=True),
                name='unique_responsavel_principal_por_aluno',
            ),
        ]

    def __str__(self):
        return f'{self.responsavel.nome} → {self.aluno.nome_completo} ({self.get_parentesco_display()})'
