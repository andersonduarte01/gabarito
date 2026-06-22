from django.db import models

from apps.core.validators import validate_cpf, normalizar_cpf


SEXO = [
    ('',  'Não informado'),
    ('M', 'Masculino'),
    ('F', 'Feminino'),
]

SITUACAO = [
    ('MATRIC',  'Matriculado(a)'),
    ('TRANSF',  'Transferido(a)'),
    ('EVADIDO', 'Evadido(a)'),
    ('OUTRO',   'Outro'),
]


class Aluno(models.Model):
    usuario = models.OneToOneField(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='aluno',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='alunos',
        verbose_name='Escola',
    )
    sala = models.ForeignKey(
        'sala.Turma',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alunos',
        verbose_name='Turma',
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        blank=True,
        default='',
        validators=[validate_cpf],
    )
    matricula = models.CharField(
        verbose_name='Matrícula',
        max_length=20,
        blank=True,
        default='',
    )
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento',
        null=True,
        blank=True,
    )
    sexo = models.CharField(
        verbose_name='Sexo',
        max_length=1,
        choices=SEXO,
        blank=True,
        default='',
    )
    telefone = models.CharField(
        verbose_name='Telefone',
        max_length=20,
        blank=True,
        default='',
    )
    responsavel_legal = models.CharField(
        verbose_name='Responsável Legal',
        max_length=150,
        blank=True,
        default='',
    )
    telefone_responsavel = models.CharField(
        verbose_name='Telefone do Responsável',
        max_length=20,
        blank=True,
        default='',
    )
    situacao = models.CharField(
        verbose_name='Situação',
        max_length=10,
        choices=SITUACAO,
        default='MATRIC',
    )

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['usuario__nome']

    def __str__(self):
        return self.usuario.nome

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        super().save(*args, **kwargs)
