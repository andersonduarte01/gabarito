from django.db import models
from apps.escola.models import UnidadeEscolar, AnoLetivo

TURNO_CHOICES = [
    ('manha',    'Manhã'),
    ('tarde',    'Tarde'),
    ('integral', 'Tempo Integral'),
]


class Serie(models.Model):
    nome   = models.CharField(verbose_name='Nome', max_length=50)
    escola = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name='Escola',
    )
    ordem = models.PositiveSmallIntegerField(
        verbose_name='Ordem',
        default=0,
        help_text='Ordem de exibição na listagem.',
    )

    class Meta:
        verbose_name        = 'Série'
        verbose_name_plural = 'Séries'
        ordering            = ['ordem', 'nome']
        unique_together     = [('nome', 'escola')]

    def __str__(self):
        return self.nome


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
    serie = models.ForeignKey(
        Serie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turmas',
        verbose_name='Série',
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
        verbose_name        = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering            = ['nome']

    def __str__(self):
        turno_label = dict(TURNO_CHOICES).get(self.turno, self.turno)
        serie_label = self.serie.nome if self.serie_id else '—'
        return f'{self.nome} — {serie_label} ({turno_label})'

    @property
    def total_alunos(self):
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
