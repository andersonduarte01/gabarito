from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.text import slugify


class TipoInstituicao(models.TextChoices):
    PUBLICA      = 'PUBLICA',      'Pública'
    PRIVADA      = 'PRIVADA',      'Privada'
    FILANTROPICA = 'FILANTROPICA', 'Filantrópica'


class TipoSegmento(models.TextChoices):
    INF = 'INF', 'Infantil'
    FI  = 'FI',  'Fundamental I'
    FII = 'FII', 'Fundamental II'
    MED = 'MED', 'Médio'
    TEC = 'TEC', 'Técnico'


class UnidadeEscolar(models.Model):
    nome           = models.CharField('Nome', max_length=200)
    nome_curto     = models.CharField('Nome Curto', max_length=60, blank=True)
    cnpj           = models.CharField('CNPJ', max_length=18, blank=True)
    slug           = models.SlugField('Slug', max_length=220, unique=True, blank=True)
    tipo           = models.CharField(
        'Tipo',
        max_length=15,
        choices=TipoInstituicao.choices,
        default=TipoInstituicao.PRIVADA,
    )
    municipio      = models.CharField('Município', max_length=100, blank=True)
    uf             = models.CharField('UF', max_length=2, blank=True)
    telefone       = models.CharField('Telefone', max_length=20, blank=True)
    email          = models.EmailField('E-mail', blank=True)
    site           = models.URLField('Site', blank=True)
    logo           = models.ImageField('Logo', upload_to='escolas/logos/', null=True, blank=True)
    cor_primaria   = models.CharField('Cor Primária', max_length=7, default='#0d6efd')
    cor_secundaria = models.CharField('Cor Secundária', max_length=7, default='#6c757d')
    cor_acento     = models.CharField('Cor Acento', max_length=7, default='#0dcaf0')
    criado_em      = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em  = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Unidade Escolar'
        verbose_name_plural = 'Unidades Escolares'
        ordering            = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._gerar_slug()
        super().save(*args, **kwargs)

    def _gerar_slug(self) -> str:
        base     = slugify(self.nome)
        slug     = base
        contador = 1
        while UnidadeEscolar.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base}-{contador}'
            contador += 1
        return slug


class SegmentoEscolar(models.Model):
    escola = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='segmentos',
        verbose_name='Escola',
    )
    tipo   = models.CharField('Tipo', max_length=5, choices=TipoSegmento.choices)

    class Meta:
        verbose_name        = 'Segmento Escolar'
        verbose_name_plural = 'Segmentos Escolares'
        unique_together     = ('escola', 'tipo')

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.escola}'


class EnderecoEscolar(models.Model):
    escola      = models.ForeignKey(
        UnidadeEscolar,
        on_delete=models.CASCADE,
        related_name='enderecos',
        verbose_name='Escola',
    )
    nome        = models.CharField(
        'Identificação',
        max_length=100,
        blank=True,
        help_text='Ex: Sede, Anexo, Quadra',
    )
    principal   = models.BooleanField('Principal', default=False)
    cep         = models.CharField('CEP', max_length=9, blank=True)
    logradouro  = models.CharField('Logradouro', max_length=200)
    numero      = models.CharField('Número', max_length=20)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro      = models.CharField('Bairro', max_length=100)
    municipio   = models.CharField('Município', max_length=100)
    uf          = models.CharField('UF', max_length=2)

    class Meta:
        verbose_name        = 'Endereço Escolar'
        verbose_name_plural = 'Endereços Escolares'
        constraints = [
            UniqueConstraint(
                fields=['escola'],
                condition=Q(principal=True),
                name='unique_endereco_principal_por_escola',
            ),
        ]

    def __str__(self):
        return f'{self.logradouro}, {self.numero} — {self.municipio}/{self.uf}'
