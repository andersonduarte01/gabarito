from django.db import models

from apps.escola.models import UnidadeEscolar, AnoLetivo


ANO_CHOICES = [
    ('Educação Infantil', 'Educação Infantil'),
    ('Pré-Escola',        'Pré-Escola'),
    ('4 Anos',            '4 Anos'),
    ('5 Anos',            '5 Anos'),
    ('Turma Unificada',   'Turma Unificada'),
    ('1º Ano',            '1º Ano'),
    ('2º Ano',            '2º Ano'),
    ('3º Ano',            '3º Ano'),
    ('4º Ano',            '4º Ano'),
    ('5º Ano',            '5º Ano'),
    ('6º Ano',            '6º Ano'),
    ('7º Ano',            '7º Ano'),
    ('8º Ano',            '8º Ano'),
    ('9º Ano',            '9º Ano'),
]

TURNO_CHOICES = [
    ('manha',    'Manhã'),
    ('tarde',    'Tarde'),
    ('integral', 'Tempo Integral'),
]


class Ano(models.Model):
    descricao = models.CharField(
        verbose_name='Ano',
        max_length=30,
        choices=ANO_CHOICES,
        unique=True,
    )

    class Meta:
        verbose_name = 'Ano'
        verbose_name_plural = 'Anos'
        ordering = ['descricao']

    def __str__(self):
        return self.descricao


class Sala(models.Model):
    descricao = models.CharField(verbose_name='Identificação da sala', max_length=100)
    escola = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='salas',
        verbose_name='Escola',
    )
    turno = models.CharField(
        verbose_name='Turno',
        max_length=10,
        choices=TURNO_CHOICES,
        default='manha',
    )
    ano = models.ForeignKey(
        Ano,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salas',
        verbose_name='Ano escolar',
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.CASCADE,
        related_name='salas',
        verbose_name='Ano letivo',
    )

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['descricao']

    def __str__(self):
        turno_label = dict(TURNO_CHOICES).get(self.turno, self.turno)
        ano_label = self.ano.descricao if self.ano else '—'
        return f'{self.descricao} — {ano_label} ({turno_label})'

    @property
    def total_alunos(self):
        return self.alunos.count()
