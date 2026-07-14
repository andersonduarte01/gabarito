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


class StatusAvaliacao(models.TextChoices):
    RASCUNHO  = 'RASCUNHO',  'Rascunho'
    PUBLICADA = 'PUBLICADA', 'Publicada'
    ENCERRADA = 'ENCERRADA', 'Encerrada'


class TipoQuestao(models.TextChoices):
    MULTIPLA_ESCOLHA    = 'MULTIPLA_ESCOLHA',    'Múltipla Escolha'
    MULTIPLAS_RESPOSTAS = 'MULTIPLAS_RESPOSTAS', 'Múltiplas Respostas'
    VERDADEIRO_FALSO    = 'VERDADEIRO_FALSO',    'Verdadeiro ou Falso'
    RESPOSTA_CURTA      = 'RESPOSTA_CURTA',      'Resposta Curta'
    DISCURSIVA          = 'DISCURSIVA',          'Discursiva'
    NUMERICA            = 'NUMERICA',            'Numérica'
    LACUNAS             = 'LACUNAS',             'Completar Lacunas'
    ASSOCIACAO          = 'ASSOCIACAO',          'Associação entre Colunas'
    ORDENACAO           = 'ORDENACAO',           'Ordenação de Itens'


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
    titulo                       = models.CharField('Título', max_length=200)
    descricao                    = models.TextField('Descrição', blank=True)
    tipo                         = models.CharField('Tipo', max_length=20, choices=TipoAvaliacao.choices)
    modalidade                   = models.CharField(
        'Modalidade', max_length=20, choices=ModalidadeAvaliacao.choices,
        default=ModalidadeAvaliacao.PRESENCIAL,
    )
    status                       = models.CharField(
        'Status', max_length=10, choices=StatusAvaliacao.choices,
        default=StatusAvaliacao.RASCUNHO,
    )
    data_aplicacao               = models.DateField('Data de Aplicação', null=True, blank=True)
    nota_maxima                  = models.DecimalField(
        'Nota Máxima', max_digits=5, decimal_places=2, default=Decimal('10.00'),
    )
    peso                         = models.DecimalField(
        'Peso', max_digits=5, decimal_places=2, default=Decimal('1.00'),
    )
    tempo_limite                 = models.PositiveIntegerField(
        'Tempo Limite (min)', null=True, blank=True,
    )
    embaralhar_questoes          = models.BooleanField('Embaralhar Questões', default=False)
    embaralhar_alternativas      = models.BooleanField('Embaralhar Alternativas', default=False)
    exibir_nota_ao_finalizar     = models.BooleanField('Exibir Nota ao Finalizar', default=False)
    exibir_gabarito_ao_finalizar = models.BooleanField('Exibir Gabarito ao Finalizar', default=False)
    criado_em                    = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering            = ['-data_aplicacao', '-criado_em']

    def __str__(self):
        return f'{self.titulo} — {self.turma} ({self.materia})'


class Questao(models.Model):
    avaliacao               = models.ForeignKey(
        Avaliacao, on_delete=models.CASCADE,
        related_name='questoes', verbose_name='Avaliação',
    )
    numero                  = models.PositiveSmallIntegerField('Número')
    titulo                  = models.CharField('Título', max_length=200, blank=True)
    enunciado               = models.TextField('Enunciado')
    descricao               = models.TextField('Descrição', blank=True)
    tipo                    = models.CharField('Tipo', max_length=20, choices=TipoQuestao.choices)
    pontuacao               = models.DecimalField('Pontuação', max_digits=5, decimal_places=2)
    obrigatoria             = models.BooleanField('Obrigatória', default=True)
    embaralhar_alternativas = models.BooleanField('Embaralhar Alternativas', default=False)
    feedback                = models.TextField('Feedback', blank=True)
    imagem                  = models.ImageField(
        'Imagem', upload_to='avaliacoes/questoes/imagens/', null=True, blank=True,
    )
    arquivo_pdf             = models.FileField(
        'PDF de Apoio', upload_to='avaliacoes/questoes/pdfs/', null=True, blank=True,
    )
    # Gabarito para tipos que não usam OpcaoResposta.correta:
    # RESPOSTA_CURTA  → {"texto": "Brasília", "case_sensitive": false}
    # NUMERICA        → {"valor": 9.8, "tolerancia": 0.1}
    # LACUNAS         → {"lacunas": ["sol", "lua"]}
    # ASSOCIACAO      → {"colunas": [...], "opcoes": [...], "pares": [["a1","b1"], ...]}
    # ORDENACAO       → ordem correta definida por OpcaoResposta.ordem
    gabarito_json           = models.JSONField('Gabarito', null=True, blank=True)

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
    imagem   = models.ImageField(
        'Imagem', upload_to='avaliacoes/opcoes/imagens/', null=True, blank=True,
    )
    # Posição correta na sequência (usado para tipo ORDENACAO)
    ordem    = models.PositiveSmallIntegerField('Ordem Correta', null=True, blank=True)
    correta  = models.BooleanField('Correta', default=False)

    class Meta:
        verbose_name        = 'Opção de Resposta'
        verbose_name_plural = 'Opções de Resposta'
        unique_together     = ('questao', 'letra')
        ordering            = ['letra']

    def __str__(self):
        return f'{self.letra}) {self.texto}'


class RespostaAluno(models.Model):
    questao         = models.ForeignKey(
        Questao, on_delete=models.CASCADE,
        related_name='respostas', verbose_name='Questão',
    )
    aluno           = models.ForeignKey(
        'aluno.Aluno', on_delete=models.CASCADE,
        related_name='respostas_avaliacao', verbose_name='Aluno',
    )
    # MULTIPLA_ESCOLHA / VERDADEIRO_FALSO → FK direto (integridade referencial preservada)
    opcao_escolhida = models.ForeignKey(
        OpcaoResposta, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='respostas', verbose_name='Opção Escolhida',
    )
    # RESPOSTA_CURTA / DISCURSIVA → texto plano
    resposta_texto  = models.TextField('Resposta Textual', blank=True)
    # Tipos estruturados:
    # MULTIPLAS_RESPOSTAS → {"opcoes": [id1, id2]}
    # NUMERICA            → {"valor": 9.8}
    # LACUNAS             → {"lacunas": ["sol", "lua"]}
    # ASSOCIACAO          → {"pares": [["a1", "b1"], ...]}
    # ORDENACAO           → {"ordem": [id2, id1, id3]}
    resposta_json   = models.JSONField('Resposta Estruturada', null=True, blank=True)
    nota_questao    = models.DecimalField(
        'Nota da Questão', max_digits=5, decimal_places=2, null=True, blank=True,
    )
    corrigida       = models.BooleanField('Corrigida', default=False)

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
