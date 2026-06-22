from django.db import models
from apps.escola.models import UnidadeEscolar, AnoLetivo

SERIE_CHOICES = [
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


class Turma(models.Model):
    nome = models.CharField(verbose_name='Nome da turma', max_length=100)
    escola = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name='Escola',
    )
    turno = models.CharField(
        verbose_name='Turno',
        max_length=10,
        choices=TURNO_CHOICES,
        default='manha',
    )
    serie = models.CharField(
        verbose_name='Série',
        max_length=30,
        choices=SERIE_CHOICES,
        blank=True,
        default='',
    )
    ano_letivo = models.ForeignKey(
        AnoLetivo,
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name='Ano letivo',
    )
    capacidade = models.PositiveSmallIntegerField(
        verbose_name='Capacidade',
        null=True,
        blank=True,
        help_text='Número máximo de alunos na turma.',
    )
    ativo = models.BooleanField(verbose_name='Ativa', default=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['nome']

    def __str__(self):
        turno_label = dict(TURNO_CHOICES).get(self.turno, self.turno)
        serie_label = self.serie or '—'
        return f'{self.nome} — {serie_label} ({turno_label})'

    @property
    def total_alunos(self):
        # usa a annotation alunos_count quando disponível (evita query extra)
        if 'alunos_count' in self.__dict__:
            return self.__dict__['alunos_count']
        return self.alunos.count()

    @property
    def vagas_disponiveis(self):
        if self.capacidade is None:
            return None
        return max(0, self.capacidade - self.total_alunos)

    @property
    def percentual_ocupacao(self):
        if not self.capacidade:
            return None
        return min(100, round(self.total_alunos * 100 / self.capacidade))

    @property
    def status(self):
        if not self.ativo:
            return 'inativa'
        if self.capacidade and self.total_alunos >= self.capacidade:
            return 'lotada'
        return 'ativa'

    @property
    def status_display(self):
        return {'ativa': 'Ativa', 'inativa': 'Inativa', 'lotada': 'Lotada'}[self.status]


# Alias para compatibilidade com apps desativados que importam Sala
Sala = Turma
