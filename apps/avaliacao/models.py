from decimal import Decimal

from django.db import models


class TipoAvaliacao(models.TextChoices):
    PROVA       = 'PROVA',       'Prova'
    TRABALHO    = 'TRABALHO',    'Trabalho'
    SEMINARIO   = 'SEMINARIO',   'Seminário'
    ATIVIDADE   = 'ATIVIDADE',   'Atividade'
    RECUPERACAO = 'RECUPERACAO', 'Recuperação'


class ModalidadeAvaliacao(models.TextChoices):
    PRESENCIAL = 'PRESENCIAL', 'Presencial'
    ONLINE     = 'ONLINE',     'Online'


class TipoQuestao(models.TextChoices):
    MULTIPLA_ESCOLHA = 'MULTIPLA_ESCOLHA', 'Múltipla Escolha'
    DISCURSIVA       = 'DISCURSIVA',       'Discursiva'


class Avaliacao(models.Model):
    escola         = models.ForeignKey(
        'escola.UnidadeEscolar', on_delete=models.CASCADE,
        related_name='avaliacoes', verbose_name='Escola',
    )
    turma          = models.ForeignKey(
        'turma.Turma', on_delete=models.PROTECT,
        related_name='avaliacoes', verbose_name='Turma',
    )
    materia        = models.ForeignKey(
        'materia.Materia', on_delete=models.PROTECT,
        related_name='avaliacoes', verbose_name='Matéria',
    )
    professor      = models.ForeignKey(
        'professor.PerfilProfessor', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='avaliacoes', verbose_name='Professor',
    )
    ano_letivo     = models.ForeignKey(
        'ano_letivo.AnoLetivo', on_delete=models.PROTECT,
        related_name='avaliacoes', verbose_name='Ano Letivo',
    )
    periodo_letivo = models.ForeignKey(
        'ano_letivo.PeriodoLetivo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='avaliacoes', verbose_name='Período Letivo',
    )
    titulo         = models.CharField('Título', max_length=200)
    tipo           = models.CharField('Tipo', max_length=20, choices=TipoAvaliacao.choices)
    modalidade     = models.CharField('Modalidade', max_length=20, choices=ModalidadeAvaliacao.choices,
                                      default=ModalidadeAvaliacao.PRESENCIAL)
    data_aplicacao = models.DateField('Data de Aplicação', null=True, blank=True)
    nota_maxima    = models.DecimalField('Nota Máxima', max_digits=5, decimal_places=2, default=Decimal('10.00'))
    peso           = models.DecimalField('Peso', max_digits=5, decimal_places=2, default=Decimal('1.00'))
    publicada      = models.BooleanField('Publicada', default=False)
    criado_em      = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering            = ['-data_aplicacao', '-criado_em']

    def __str__(self):
        return f'{self.titulo} — {self.turma} ({self.materia})'


class Questao(models.Model):
    avaliacao  = models.ForeignKey(
        Avaliacao, on_delete=models.CASCADE,
        related_name='questoes', verbose_name='Avaliação',
    )
    numero     = models.PositiveSmallIntegerField('Número')
    enunciado  = models.TextField('Enunciado')
    tipo       = models.CharField('Tipo', max_length=20, choices=TipoQuestao.choices)
    pontuacao  = models.DecimalField('Pontuação', max_digits=5, decimal_places=2)

    class Meta:
        verbose_name        = 'Questão'
        verbose_name_plural = 'Questões'
        unique_together     = ('avaliacao', 'numero')
        ordering            = ['numero']

    def __str__(self):
        return f'Q{self.numero} — {self.avaliacao.titulo}'


class OpcaoResposta(models.Model):
    questao  = models.ForeignKey(
        Questao, on_delete=models.CASCADE,
        related_name='opcoes', verbose_name='Questão',
    )
    letra    = models.CharField('Letra', max_length=1)
    texto    = models.CharField('Texto', max_length=500)
    correta  = models.BooleanField('Correta', default=False)

    class Meta:
        verbose_name        = 'Opção de Resposta'
        verbose_name_plural = 'Opções de Resposta'
        unique_together     = ('questao', 'letra')
        ordering            = ['letra']

    def __str__(self):
        return f'{self.letra}) {self.texto}'


class RespostaAluno(models.Model):
    questao          = models.ForeignKey(
        Questao, on_delete=models.CASCADE,
        related_name='respostas', verbose_name='Questão',
    )
    aluno            = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='respostas_avaliacao', verbose_name='Aluno',
    )
    opcao_escolhida  = models.ForeignKey(
        OpcaoResposta, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='respostas', verbose_name='Opção Escolhida',
    )
    resposta_texto   = models.TextField('Resposta Textual', blank=True)
    nota_questao     = models.DecimalField('Nota da Questão', max_digits=5, decimal_places=2,
                                           null=True, blank=True)
    corrigida        = models.BooleanField('Corrigida', default=False)

    class Meta:
        verbose_name        = 'Resposta do Aluno'
        verbose_name_plural = 'Respostas dos Alunos'
        unique_together     = ('questao', 'aluno')

    def __str__(self):
        return f'{self.aluno.nome_completo} — Q{self.questao.numero}'


class NotaAluno(models.Model):
    avaliacao  = models.ForeignKey(
        Avaliacao, on_delete=models.CASCADE,
        related_name='notas', verbose_name='Avaliação',
    )
    aluno      = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='notas_avaliacao', verbose_name='Aluno',
    )
    nota       = models.DecimalField('Nota', max_digits=5, decimal_places=2, null=True, blank=True)
    ausente    = models.BooleanField('Ausente', default=False)
    observacao = models.TextField('Observação', blank=True)
    lancado_em = models.DateTimeField('Lançado em', auto_now=True)

    class Meta:
        verbose_name        = 'Nota do Aluno'
        verbose_name_plural = 'Notas dos Alunos'
        unique_together     = ('avaliacao', 'aluno')

    def __str__(self):
        return f'{self.aluno.nome_completo} — {self.avaliacao.titulo}: {self.nota}'
