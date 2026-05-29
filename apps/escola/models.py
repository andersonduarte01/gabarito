from django.db import models
from django.utils.text import slugify

from apps.core.validators import validate_cnpj, validate_telefone, normalizar_cnpj, normalizar_telefone


class UnidadeEscolar(models.Model):

    MUNICIPAL = 'MUN'
    ESTADUAL  = 'EST'
    FEDERAL   = 'FED'
    PRIVADA   = 'PRIV'

    TIPO_CHOICES = [
        (MUNICIPAL, 'Municipal'),
        (ESTADUAL,  'Estadual'),
        (FEDERAL,   'Federal'),
        (PRIVADA,   'Privada'),
    ]

    nome_escola  = models.CharField(verbose_name='Nome da Escola', max_length=200)
    slug         = models.SlugField(verbose_name='Slug', max_length=220, unique=True, blank=True)
    tipo         = models.CharField(
        verbose_name='Tipo',
        max_length=4,
        choices=TIPO_CHOICES,
        default=MUNICIPAL,
    )
    logo_escola  = models.ImageField(
        verbose_name='Logo',
        upload_to='Imagens/Logo',
        null=True,
        blank=True,
    )
    inep         = models.CharField(verbose_name='Código INEP', max_length=20, null=True, blank=True)
    cnpj         = models.CharField(
        verbose_name='CNPJ',
        max_length=14,
        null=True,
        blank=True,
        validators=[validate_cnpj],
    )
    telefone     = models.CharField(
        verbose_name='Telefone',
        max_length=20,
        blank=True,
        validators=[validate_telefone],
    )
    email        = models.EmailField(verbose_name='Email', blank=True)
    site         = models.URLField(verbose_name='Site', blank=True)
    ativo        = models.BooleanField(verbose_name='Ativa', default=True)
    criado_em    = models.DateTimeField(verbose_name='Criada em', auto_now_add=True)
    atualizado_em = models.DateTimeField(verbose_name='Atualizada em', auto_now=True)

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        ordering = ['nome_escola']

    def __str__(self):
        return self.nome_escola

    def save(self, *args, **kwargs):
        if self.cnpj:
            self.cnpj = normalizar_cnpj(self.cnpj)
        if self.telefone:
            self.telefone = normalizar_telefone(self.telefone)
        if not self.slug:
            self.slug = self._gerar_slug()
        super().save(*args, **kwargs)

    def _gerar_slug(self) -> str:
        base = slugify(self.nome_escola)
        slug = base
        contador = 1
        while UnidadeEscolar.objects.filter(slug=slug).exists():
            slug = f'{base}-{contador}'
            contador += 1
        return slug

    def tem_logo(self) -> bool:
        return bool(self.logo_escola)

    @property
    def endereco(self):
        return getattr(self, '_endereco_cache', None) or EnderecoEscolar.objects.filter(escola=self).first()

    @property
    def ano_letivo_corrente(self):
        return self.anos_letivos.filter(corrente=True).first()


class EnderecoEscolar(models.Model):
    escola       = models.OneToOneField(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='endereco_obj',
        verbose_name='Escola',
    )
    rua          = models.CharField(verbose_name='Rua', max_length=100)
    numero       = models.CharField(verbose_name='Número', max_length=20)
    complemento  = models.CharField(verbose_name='Complemento', max_length=200, blank=True)
    bairro       = models.CharField(verbose_name='Bairro', max_length=100)
    cep          = models.CharField(verbose_name='CEP', max_length=10)
    cidade       = models.CharField(verbose_name='Cidade', max_length=100)
    estado       = models.CharField(verbose_name='Estado', max_length=30)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'{self.rua}, {self.numero} — {self.cidade}/{self.estado}'


class AnoLetivo(models.Model):
    escola    = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='anos_letivos',
        verbose_name='Escola',
    )
    ano       = models.IntegerField(verbose_name='Ano Letivo')
    inicio    = models.DateField(verbose_name='Início')
    fim       = models.DateField(verbose_name='Fim')
    corrente  = models.BooleanField(verbose_name='Ano Corrente', default=False)
    descricao = models.TextField(verbose_name='Descrição', blank=True)

    class Meta:
        verbose_name = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'
        unique_together = ('escola', 'ano')
        ordering = ['-ano']

    def __str__(self):
        return f'{self.ano} — {self.escola.nome_escola}'

    def save(self, *args, **kwargs):
        if self.corrente:
            AnoLetivo.objects.filter(escola=self.escola, corrente=True).exclude(pk=self.pk).update(corrente=False)
        super().save(*args, **kwargs)
