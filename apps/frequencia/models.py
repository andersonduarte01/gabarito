from django.db import models


class RegistroFrequencia(models.Model):
    turma        = models.ForeignKey(
        'turma.Turma', on_delete=models.CASCADE,
        related_name='registros_frequencia', verbose_name='Turma',
    )
    materia      = models.ForeignKey(
        'materia.Materia', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_frequencia', verbose_name='Matéria',
    )
    professor    = models.ForeignKey(
        'professor.PerfilProfessor', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_frequencia', verbose_name='Professor',
    )
    ano_letivo   = models.ForeignKey(
        'ano_letivo.AnoLetivo', on_delete=models.CASCADE,
        related_name='registros_frequencia', verbose_name='Ano Letivo',
    )
    periodo_letivo = models.ForeignKey(
        'ano_letivo.PeriodoLetivo', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_frequencia', verbose_name='Período Letivo',
    )
    data         = models.DateField('Data da Aula')
    criado_em    = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por   = models.ForeignKey(
        'core.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_frequencia_criados', verbose_name='Criado por',
    )

    class Meta:
        verbose_name        = 'Registro de Frequência'
        verbose_name_plural = 'Registros de Frequência'
        ordering            = ['-data', '-criado_em']

    def __str__(self):
        materia = self.materia.nome if self.materia else '—'
        return f'{self.turma.nome} | {materia} | {self.data}'


class PresencaAluno(models.Model):
    registro     = models.ForeignKey(
        RegistroFrequencia, on_delete=models.CASCADE,
        related_name='presencas', verbose_name='Registro',
    )
    aluno        = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='presencas', verbose_name='Aluno',
    )
    presente     = models.BooleanField('Presente', default=True)
    justificado  = models.BooleanField('Justificado', default=False)
    observacao   = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name        = 'Presença'
        verbose_name_plural = 'Presenças'
        unique_together     = ('registro', 'aluno')
        ordering            = ['aluno__nome_completo']

    def __str__(self):
        status = 'P' if self.presente else ('FJ' if self.justificado else 'F')
        return f'{self.aluno.nome_completo} [{status}] — {self.registro}'
