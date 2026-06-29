from django.db import models


class Serie(models.Model):
    escola   = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name='Escola',
    )
    segmento = models.ForeignKey(
        'escola.SegmentoEscolar',
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name='Segmento',
    )
    nome  = models.CharField('Nome', max_length=100)
    ordem = models.PositiveSmallIntegerField('Ordem')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name        = 'Série'
        verbose_name_plural = 'Séries'
        unique_together     = ('escola', 'segmento', 'nome')
        ordering            = ['segmento__tipo', 'ordem']

    def __str__(self):
        return f'{self.nome} — {self.segmento.get_tipo_display()}'
