from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from unidecode import unidecode


class Categoria(models.Model):
    titulo = models.CharField(max_length=100, verbose_name='Título')
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class PublicadosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Noticia.PUBLICADO)


class Noticia(models.Model):
    RASCUNHO = 'RASCUNHO'
    PUBLICADO = 'PUBLICADO'
    STATUS = [
        (RASCUNHO, 'Rascunho'),
        (PUBLICADO, 'Publicado'),
    ]

    PUBLICA = 'PUB'
    PRIVADA = 'PRIV'
    VISIBILIDADE = [
        (PUBLICA, 'Pública'),
        (PRIVADA, 'Privada'),
    ]

    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='noticias',
        verbose_name='Escola',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    resumo = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Resumo',
        help_text='Exibido nos cards. Se vazio, será extraído do conteúdo automaticamente.',
    )
    conteudo = RichTextUploadingField(verbose_name='Conteúdo')
    imagem = models.ImageField(
        upload_to='blog/',
        null=True,
        blank=True,
        verbose_name='Imagem de capa',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Autor',
        related_name='noticias',
    )
    visibilidade = models.CharField(
        max_length=4,
        choices=VISIBILIDADE,
        default=PUBLICA,
        db_index=True,
        verbose_name='Visibilidade',
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoria',
        related_name='noticias',
    )
    slug = models.SlugField(max_length=220, unique=True, blank=True, editable=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default=RASCUNHO,
        verbose_name='Status',
        db_index=True,
    )
    destaque = models.BooleanField(default=False, verbose_name='Destaque')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    objects = models.Manager()
    publicados = PublicadosManager()

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('blog:noticia', kwargs={'slug': self.slug})

    def get_resumo(self):
        if self.resumo:
            return self.resumo
        return strip_tags(self.conteudo)[:280]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._gerar_slug_unico()
        super().save(*args, **kwargs)

    def _gerar_slug_unico(self):
        base = slugify(unidecode(self.titulo)) or 'noticia'
        slug = base
        n = 1
        qs = Noticia.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug


