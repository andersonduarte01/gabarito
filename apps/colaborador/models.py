from django.db import models


class TipoVinculoEmpregaticio(models.TextChoices):
    CLT         = 'CLT',         'CLT'
    ESTATUTARIO = 'ESTATUTARIO', 'Estatutário'
    TEMPORARIO  = 'TEMPORARIO',  'Temporário'
    AUTONOMO    = 'AUTONOMO',    'Autônomo'


class FuncaoEscolar(models.Model):
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='funcoes',
        verbose_name='Escola',
    )
    nome  = models.CharField('Nome', max_length=100)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Função Escolar'
        verbose_name_plural = 'Funções Escolares'
        unique_together     = ('escola', 'nome')
        ordering            = ['nome']

    def __str__(self):
        return self.nome


class PerfilColaborador(models.Model):
    papel           = models.OneToOneField(
        'core.PapelVinculo',
        on_delete=models.CASCADE,
        related_name='perfil_colaborador',
        verbose_name='Papel',
    )
    funcao          = models.ForeignKey(
        FuncaoEscolar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='colaboradores',
        verbose_name='Função',
    )
    endereco        = models.OneToOneField(
        'core.Endereco',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_colaborador',
        verbose_name='Endereço',
    )
    cpf             = models.CharField('CPF', max_length=14, blank=True)
    rg              = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    telefone        = models.CharField('Telefone', max_length=20, blank=True)
    foto            = models.ImageField('Foto', upload_to='colaboradores/fotos/', null=True, blank=True)
    data_admissao   = models.DateField('Data de Admissão', null=True, blank=True)
    tipo_vinculo    = models.CharField(
        'Tipo de Vínculo',
        max_length=20,
        choices=TipoVinculoEmpregaticio.choices,
        default=TipoVinculoEmpregaticio.CLT,
    )
    pis             = models.CharField('PIS/PASEP', max_length=20, blank=True)
    criado_em       = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em   = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Perfil do Colaborador'
        verbose_name_plural = 'Perfis de Colaboradores'

    def __str__(self):
        return f'{self.papel.usuario.nome} — {self.papel.escola}'

    @property
    def escola(self):
        return self.papel.escola

    @property
    def usuario(self):
        return self.papel.usuario
