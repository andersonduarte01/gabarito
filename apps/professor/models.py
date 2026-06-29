from django.db import models


class NivelFormacao(models.TextChoices):
    GRADUACAO      = 'GRADUACAO',      'Graduação'
    ESPECIALIZACAO = 'ESPECIALIZACAO', 'Especialização'
    MESTRADO       = 'MESTRADO',       'Mestrado'
    DOUTORADO      = 'DOUTORADO',      'Doutorado'
    OUTRO          = 'OUTRO',          'Outro'


class TipoVinculoProfessor(models.TextChoices):
    CLT         = 'CLT',         'CLT'
    ESTATUTARIO = 'ESTATUTARIO', 'Estatutário'
    TEMPORARIO  = 'TEMPORARIO',  'Temporário'
    AUTONOMO    = 'AUTONOMO',    'Autônomo'


class PerfilProfessor(models.Model):
    papel                = models.OneToOneField(
        'core.PapelVinculo',
        on_delete=models.CASCADE,
        related_name='perfil_professor',
        verbose_name='Papel',
    )
    endereco             = models.OneToOneField(
        'core.Endereco',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='perfil_professor',
        verbose_name='Endereço',
    )
    cpf                  = models.CharField('CPF', max_length=14, blank=True)
    rg                   = models.CharField('RG', max_length=20, blank=True)
    data_nascimento      = models.DateField('Data de Nascimento', null=True, blank=True)
    telefone             = models.CharField('Telefone', max_length=20, blank=True)
    foto                 = models.ImageField('Foto', upload_to='professores/fotos/', null=True, blank=True)
    data_admissao        = models.DateField('Data de Admissão', null=True, blank=True)
    tipo_vinculo         = models.CharField(
        'Tipo de Vínculo', max_length=20,
        choices=TipoVinculoProfessor.choices,
        default=TipoVinculoProfessor.CLT,
    )
    registro_profissional = models.CharField('Registro Profissional', max_length=50, blank=True)
    criado_em            = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em        = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Perfil do Professor'
        verbose_name_plural = 'Perfis de Professores'

    def __str__(self):
        return f'{self.papel.usuario.nome} — {self.papel.escola}'

    @property
    def escola(self):
        return self.papel.escola

    @property
    def usuario(self):
        return self.papel.usuario


class FormacaoAcademica(models.Model):
    professor     = models.ForeignKey(
        PerfilProfessor,
        on_delete=models.CASCADE,
        related_name='formacoes',
        verbose_name='Professor',
    )
    nivel         = models.CharField('Nível', max_length=20, choices=NivelFormacao.choices)
    curso         = models.CharField('Curso', max_length=200)
    instituicao   = models.CharField('Instituição', max_length=200)
    ano_conclusao = models.PositiveSmallIntegerField('Ano de Conclusão', null=True, blank=True)

    class Meta:
        verbose_name        = 'Formação Acadêmica'
        verbose_name_plural = 'Formações Acadêmicas'
        ordering            = ['-ano_conclusao', 'nivel']

    def __str__(self):
        return f'{self.get_nivel_display()} em {self.curso} — {self.instituicao}'
