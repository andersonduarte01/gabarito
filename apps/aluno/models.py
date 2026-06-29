from django.db import models


class SituacaoMatricula(models.TextChoices):
    MATRICULADO = 'MATRICULADO', 'Matriculado'
    TRANSFERIDO = 'TRANSFERIDO', 'Transferido'
    EVADIDO     = 'EVADIDO',     'Evadido'
    CONCLUINTE  = 'CONCLUINTE',  'Concluinte'


class Aluno(models.Model):
    escola          = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='alunos',
        verbose_name='Escola',
    )
    usuario         = models.OneToOneField(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='aluno',
        verbose_name='Usuário',
    )
    endereco        = models.OneToOneField(
        'core.Endereco',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='aluno',
        verbose_name='Endereço',
    )
    matricula       = models.CharField('Matrícula', max_length=20)
    nome_completo   = models.CharField('Nome Completo', max_length=200)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    cpf             = models.CharField('CPF', max_length=14, blank=True)
    rg              = models.CharField('RG', max_length=20, blank=True)
    foto            = models.ImageField('Foto', upload_to='alunos/fotos/', null=True, blank=True)
    ativo           = models.BooleanField('Ativo', default=True)
    criado_em       = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em   = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Aluno'
        verbose_name_plural = 'Alunos'
        unique_together     = ('escola', 'matricula')
        ordering            = ['nome_completo']

    def __str__(self):
        return f'{self.nome_completo} ({self.matricula})'


class MatriculaTurma(models.Model):
    aluno          = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name='Aluno',
    )
    turma          = models.ForeignKey(
        'turma.Turma',
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name='Turma',
    )
    ano_letivo     = models.ForeignKey(
        'ano_letivo.AnoLetivo',
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name='Ano Letivo',
    )
    data_matricula = models.DateField('Data de Matrícula', auto_now_add=True)
    situacao       = models.CharField(
        'Situação', max_length=20,
        choices=SituacaoMatricula.choices,
        default=SituacaoMatricula.MATRICULADO,
    )
    ativo          = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Matrícula na Turma'
        verbose_name_plural = 'Matrículas nas Turmas'
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'ano_letivo'],
                condition=models.Q(ativo=True),
                name='unique_matricula_ativa_por_ano',
            ),
        ]

    def __str__(self):
        return f'{self.aluno.nome_completo} → {self.turma} ({self.ano_letivo.ano})'
