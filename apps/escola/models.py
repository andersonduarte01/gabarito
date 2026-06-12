from django.db import models
from django.utils.text import slugify
from stdimage import StdImageField


class UnidadeEscolar(models.Model):
    """
    Entidade tenant do SaaS. Independente do modelo de autenticação —
    usuários são vinculados via UsuarioEscola.
    """
    nome_escola = models.CharField(verbose_name='Escola', max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo_escola = StdImageField(
        upload_to='Imagens/Logo',
        variations={'thumbnail': {'width': 716, 'height': 716}},
        null=True, blank=True,
        delete_orphans=True,
    )
    inep = models.CharField(verbose_name='INEP', max_length=20, null=True, blank=True)
    cnpj = models.CharField(verbose_name='CNPJ', max_length=25, null=True, blank=True)
    telefone = models.CharField(verbose_name='Telefone', max_length=20, blank=True)
    ativa = models.BooleanField(verbose_name='Ativa', default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nome_escola)
            slug, n = base, 1
            while UnidadeEscolar.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_escola

    def tem_logo(self):
        return bool(self.logo_escola)

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        ordering = ['nome_escola']


class EnderecoEscolar(models.Model):
    escola = models.OneToOneField(
        UnidadeEscolar, on_delete=models.CASCADE, related_name='endereco'
    )
    rua = models.CharField(verbose_name='Rua', max_length=100)
    numero = models.CharField(verbose_name='Número', max_length=20)
    complemento = models.CharField(verbose_name='Complemento', max_length=200, blank=True)
    bairro = models.CharField(verbose_name='Bairro', max_length=100)
    cep = models.CharField(verbose_name='CEP', max_length=10)
    cidade = models.CharField(verbose_name='Cidade', max_length=100)
    estado = models.CharField(verbose_name='Estado', max_length=30)

    def __str__(self):
        return f"{self.escola.nome_escola} — {self.cidade}/{self.estado}"

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'


class AnoLetivo(models.Model):
    ano = models.IntegerField(verbose_name='Ano Letivo', unique=True)
    inicio = models.DateField(verbose_name='Início')
    fim = models.DateField(verbose_name='Fim')
    corrente = models.BooleanField(verbose_name='Ano Corrente', default=False)
    descricao = models.TextField(verbose_name='Descrição', blank=True)

    def __str__(self):
        return f'Ano Letivo {self.ano}'

    def save(self, *args, **kwargs):
        if self.corrente:
            AnoLetivo.objects.exclude(pk=self.pk).filter(corrente=True).update(corrente=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'
        ordering = ['-ano']


# ── Through model — vínculo usuário ↔ escola ──────────────────────────────

class UsuarioEscola(models.Model):
    """
    Coração do multi-tenancy: um usuário pode estar em várias escolas
    com papéis diferentes em cada uma.
    """

    ADMINISTRADOR = 'ADM'
    PROFESSOR     = 'PROF'
    FUNCIONARIO   = 'FUNC'
    ALUNO         = 'ALN'

    TIPOS = [
        (ADMINISTRADOR, 'Administrador'),
        (PROFESSOR,     'Professor'),
        (FUNCIONARIO,   'Funcionário'),
        (ALUNO,         'Aluno'),
    ]

    usuario = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='vinculos',
        verbose_name='Usuário',
    )
    escola = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='vinculos',
        verbose_name='Escola',
    )
    tipo = models.CharField(
        verbose_name='Tipo',
        max_length=5,
        choices=TIPOS,
    )
    ativo = models.BooleanField(verbose_name='Ativo', default=True)
    data_vinculo = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'escola')
        verbose_name = 'Vínculo Usuário-Escola'
        verbose_name_plural = 'Vínculos Usuário-Escola'
        indexes = [
            models.Index(fields=['usuario', 'ativo']),
            models.Index(fields=['escola', 'tipo', 'ativo']),
        ]

    def __str__(self):
        return f"{self.usuario.nome} — {self.escola.nome_escola} ({self.get_tipo_display()})"

    @property
    def is_admin(self):
        return self.tipo == self.ADMINISTRADOR

    @property
    def is_professor(self):
        return self.tipo == self.PROFESSOR

    @property
    def is_funcionario(self):
        return self.tipo == self.FUNCIONARIO

    @property
    def is_aluno(self):
        return self.tipo == self.ALUNO
