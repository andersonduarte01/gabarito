from django.db import models


class Materia(models.Model):
    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='materias',
        verbose_name='Escola',
    )
    nome   = models.CharField('Nome', max_length=100)
    codigo = models.CharField('Código', max_length=10, blank=True)
    ativo  = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Matéria'
        verbose_name_plural = 'Matérias'
        unique_together     = ('escola', 'nome')
        ordering            = ['nome']

    def __str__(self):
        return self.nome


class MateriaSerieConfig(models.Model):
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='series_config',
        verbose_name='Matéria',
    )
    serie = models.ForeignKey(
        'serie.Serie',
        on_delete=models.CASCADE,
        related_name='materias_config',
        verbose_name='Série',
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Vínculo Matéria-Série'
        verbose_name_plural = 'Vínculos Matéria-Série'
        unique_together     = ('materia', 'serie')

    def __str__(self):
        return f'{self.materia.nome} — {self.serie.nome}'
