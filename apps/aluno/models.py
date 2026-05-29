from django.db import models

from apps.core.validators import validate_cpf, normalizar_cpf


SEXO = [
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
        'sala.Sala',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alunos',
        verbose_name='Sala',
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        blank=True,
        validators=[validate_cpf],
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
        default='M',
    )
    responsavel_legal = models.CharField(
        verbose_name='Responsável Legal',
        max_length=150,
        blank=True,
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

    @property
    def nome(self):
        return self.usuario.nome

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = normalizar_cpf(self.cpf)
        super().save(*args, **kwargs)
