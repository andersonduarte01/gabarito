from django.db import models


class Turno(models.TextChoices):
    MATUTINO   = 'MATUTINO',   'Matutino'
    VESPERTINO = 'VESPERTINO', 'Vespertino'
    NOTURNO    = 'NOTURNO',    'Noturno'
    INTEGRAL   = 'INTEGRAL',   'Integral'


class Turma(models.Model):
    escola      = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name='Escola',
    )
    ano_letivo  = models.ForeignKey(
        'ano_letivo.AnoLetivo',
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name='Ano Letivo',
    )
    serie       = models.ForeignKey(
        'serie.Serie',
        on_delete=models.PROTECT,
        related_name='turmas',
        verbose_name='Série',
    )
    nome        = models.CharField('Nome / Identificador', max_length=50)
    turno       = models.CharField('Turno', max_length=20, choices=Turno.choices)
    capacidade  = models.PositiveIntegerField('Capacidade', null=True, blank=True)
    ativo       = models.BooleanField('Ativa', default=True)

    class Meta:
        verbose_name        = 'Turma'
        verbose_name_plural = 'Turmas'
        unique_together     = ('escola', 'ano_letivo', 'serie', 'nome', 'turno')
        ordering            = ['serie__ordem', 'nome', 'turno']

    def __str__(self):
        return f'{self.serie.nome} — {self.nome} ({self.get_turno_display()})'


class ProfessorTurma(models.Model):
    """Modo INF/FI — professor responsável pela turma inteira."""
    professor  = models.ForeignKey(
        'professor.PerfilProfessor',
        on_delete=models.CASCADE,
        related_name='professor_turmas',
        verbose_name='Professor',
    )
    turma      = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='professor_turma',
        verbose_name='Turma',
    )
    ano_letivo = models.ForeignKey(
        'ano_letivo.AnoLetivo',
        on_delete=models.CASCADE,
        related_name='professor_turmas',
        verbose_name='Ano Letivo',
    )
    ativo      = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Professor da Turma'
        verbose_name_plural = 'Professores das Turmas'
        unique_together     = ('turma', 'ano_letivo')

    def __str__(self):
        return f'{self.professor} → {self.turma} ({self.ano_letivo.ano})'


class ProfessorMateriaTurma(models.Model):
    """Modo FII/MED/TEC — professor leciona matéria específica na turma."""
    professor  = models.ForeignKey(
        'professor.PerfilProfessor',
        on_delete=models.CASCADE,
        related_name='professor_materia_turmas',
        verbose_name='Professor',
    )
    materia    = models.ForeignKey(
        'materia.Materia',
        on_delete=models.CASCADE,
        related_name='professor_materia_turmas',
        verbose_name='Matéria',
    )
    turma      = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='professor_materia_turmas',
        verbose_name='Turma',
    )
    ano_letivo = models.ForeignKey(
        'ano_letivo.AnoLetivo',
        on_delete=models.CASCADE,
        related_name='professor_materia_turmas',
        verbose_name='Ano Letivo',
    )
    ativo      = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Professor–Matéria–Turma'
        verbose_name_plural = 'Professores–Matérias–Turmas'
        unique_together     = ('materia', 'turma', 'ano_letivo')

    def __str__(self):
        return f'{self.professor} → {self.materia} / {self.turma} ({self.ano_letivo.ano})'


class PeriodoAula(models.Model):
    """Slot de aula configurado por escola (base para HorarioAula)."""
    escola      = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='periodos_aula',
        verbose_name='Escola',
    )
    numero      = models.PositiveSmallIntegerField('Número do Período')
    nome        = models.CharField('Nome', max_length=50)
    hora_inicio = models.TimeField('Hora de Início')
    hora_fim    = models.TimeField('Hora de Fim')
    turno       = models.CharField('Turno', max_length=20, choices=Turno.choices)
    ativo       = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Período de Aula'
        verbose_name_plural = 'Períodos de Aula'
        unique_together     = ('escola', 'numero', 'turno')
        ordering            = ['turno', 'numero']

    def __str__(self):
        return f'{self.nome} ({self.hora_inicio:%H:%M}–{self.hora_fim:%H:%M})'


class DiaSemana(models.IntegerChoices):
    SEGUNDA  = 1, 'Segunda-feira'
    TERCA    = 2, 'Terça-feira'
    QUARTA   = 3, 'Quarta-feira'
    QUINTA   = 4, 'Quinta-feira'
    SEXTA    = 5, 'Sexta-feira'
    SABADO   = 6, 'Sábado'


class HorarioAula(models.Model):
    """Slot de aula real: turma × período × dia × professor × matéria."""
    turma      = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Turma',
    )
    periodo    = models.ForeignKey(
        PeriodoAula,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Período',
    )
    dia_semana = models.IntegerField('Dia da Semana', choices=DiaSemana.choices)
    materia    = models.ForeignKey(
        'materia.Materia',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='horarios',
        verbose_name='Matéria',
    )
    professor  = models.ForeignKey(
        'professor.PerfilProfessor',
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Professor',
    )
    ano_letivo = models.ForeignKey(
        'ano_letivo.AnoLetivo',
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Ano Letivo',
    )
    ativo      = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Horário de Aula'
        verbose_name_plural = 'Horários de Aula'
        constraints = [
            models.UniqueConstraint(
                fields=['turma', 'periodo', 'dia_semana', 'ano_letivo'],
                name='unique_horario_turma',
            ),
            models.UniqueConstraint(
                fields=['professor', 'periodo', 'dia_semana', 'ano_letivo'],
                name='unique_horario_professor',
            ),
        ]

    def __str__(self):
        return f'{self.turma} — {self.get_dia_semana_display()} {self.periodo}'
