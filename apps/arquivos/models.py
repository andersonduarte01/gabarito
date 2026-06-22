import logging
import os
import unicodedata

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from ..sala.models import SERIE_CHOICES

try:
    from unidecode import unidecode as _unidecode
except ImportError:
    def _unidecode(s):
        return s

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utilitário de slug
# ---------------------------------------------------------------------------

def _slug_unico(modelo, titulo, pk=None):
    base = slugify(_unidecode(titulo)) or 'item'
    slug, n = base, 1
    qs = modelo.objects.all()
    if pk:
        qs = qs.exclude(pk=pk)
    while qs.filter(slug=slug).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------

class CategoriaArquivo(models.Model):
    titulo = models.CharField(max_length=100, verbose_name='Título')
    slug = models.SlugField(max_length=120, unique=True, blank=True, editable=False)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unico(CategoriaArquivo, self.titulo, self.pk)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Arquivo
# ---------------------------------------------------------------------------

class PublicosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publico=True)


class Arquivo(models.Model):
    PUBLICA = 'PUB'
    PRIVADA = 'PRIV'
    VISIBILIDADE = [
        (PUBLICA, 'Pública'),
        (PRIVADA, 'Privada'),
    ]

    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='arquivos',
        verbose_name='Escola',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='arquivos_criados',
        verbose_name='Autor',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    slug = models.SlugField(max_length=220, unique=True, blank=True, editable=False)
    pdf = models.FileField(upload_to='arquivos/', verbose_name='Arquivo PDF')
    pdf_miniatura = models.ImageField(
        upload_to='miniaturas/', blank=True, verbose_name='Miniatura',
    )
    publico = models.BooleanField(default=True, verbose_name='Público', db_index=True)
    visibilidade = models.CharField(
        max_length=4,
        choices=VISIBILIDADE,
        default=PUBLICA,
        db_index=True,
        verbose_name='Visibilidade',
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    objects = models.Manager()
    publicos = PublicosManager()

    class Meta:
        verbose_name = 'Arquivo'
        verbose_name_plural = 'Arquivos'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unico(Arquivo, self.titulo, self.pk)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Livro
# ---------------------------------------------------------------------------

class Livro(models.Model):
    PUBLICA = 'PUB'
    PRIVADA = 'PRIV'
    VISIBILIDADE = [
        (PUBLICA, 'Pública'),
        (PRIVADA, 'Privada'),
    ]

    escola = models.ForeignKey(
        'escola.UnidadeEscolar',
        on_delete=models.CASCADE,
        related_name='livros',
        verbose_name='Escola',
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    slug = models.SlugField(max_length=220, unique=True, blank=True, editable=False)
    categoria = models.ForeignKey(
        CategoriaArquivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livros',
        verbose_name='Categoria',
    )
    autor = models.CharField(max_length=200, verbose_name='Autor')
    editora = models.CharField(max_length=200, blank=True, verbose_name='Editora')
    ano_referencia = models.CharField(
        verbose_name='Ano de Referência',
        max_length=30,
        choices=SERIE_CHOICES,
        blank=True,
        default='',
    )
    pdf = models.FileField(upload_to='livros/', verbose_name='Arquivo PDF')
    pdf_miniatura = models.ImageField(
        upload_to='miniaturas/', blank=True, verbose_name='Miniatura',
    )
    visibilidade = models.CharField(
        max_length=4,
        choices=VISIBILIDADE,
        default=PUBLICA,
        db_index=True,
        verbose_name='Visibilidade',
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unico(Livro, self.titulo, self.pk)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Vídeo
# ---------------------------------------------------------------------------

class Video(models.Model):
    numero = models.CharField(
        max_length=20, blank=True, verbose_name='Número de ordem',
    )
    titulo = models.CharField(max_length=255, verbose_name='Título')
    url_video = models.URLField(max_length=500, verbose_name='URL do vídeo')
    ano = models.CharField(
        verbose_name='Ano escolar',
        max_length=30,
        choices=SERIE_CHOICES,
        blank=True,
        default='',
    )
    materia = models.CharField(
        max_length=100, blank=True, verbose_name='Matéria',
    )
    sigla = models.CharField(
        max_length=20, blank=True, verbose_name='Sigla da matéria',
    )
    professor = models.CharField(
        max_length=200, blank=True, verbose_name='Professor(a)',
    )
    duracao = models.CharField(
        max_length=20, blank=True, verbose_name='Duração',
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'
        ordering = ['numero', 'titulo']

    def __str__(self):
        return self.titulo


# ---------------------------------------------------------------------------
# Signals — geração automática de miniatura do PDF
# ---------------------------------------------------------------------------

def _nome_normalizado(texto):
    nome = unicodedata.normalize('NFD', texto)
    return nome.encode('ascii', 'ignore').decode('utf-8').strip()


def _gerar_miniatura(pdf_path, nome_base, tamanho, dpi=150):
    try:
        from pdf2image import convert_from_path
    except ImportError:
        logger.warning('pdf2image não instalado — geração de miniatura ignorada.')
        return None, None

    try:
        save_dir = os.path.join(settings.MEDIA_ROOT, 'miniaturas')
        os.makedirs(save_dir, exist_ok=True)

        imagens = convert_from_path(
            pdf_path, dpi=dpi, output_folder=save_dir,
            fmt='jpeg', first_page=1, last_page=1, size=tamanho,
        )
        with open(imagens[0].filename, 'rb') as f:
            conteudo = ContentFile(f.read())

        nome = _nome_normalizado(nome_base) or 'miniatura'
        return nome, conteudo

    except Exception as exc:
        logger.error('Falha ao gerar miniatura para "%s": %s', pdf_path, exc)
        return None, None


@receiver(post_save, sender=Arquivo)
def gerar_miniatura_arquivo(sender, instance, **kwargs):
    # Ignora se disparado pelo próprio update de miniatura
    if kwargs.get('update_fields') == frozenset({'pdf_miniatura'}):
        return
    if not instance.pdf or instance.pdf_miniatura:
        return

    nome, conteudo = _gerar_miniatura(instance.pdf.path, instance.titulo, (200, 280))
    if nome and conteudo:
        instance.pdf_miniatura.save(f'{nome}.jpeg', conteudo, save=False)
        Arquivo.objects.filter(pk=instance.pk).update(
            pdf_miniatura=instance.pdf_miniatura.name
        )


@receiver(post_save, sender=Livro)
def gerar_miniatura_livro(sender, instance, **kwargs):
    if kwargs.get('update_fields') == frozenset({'pdf_miniatura'}):
        return
    if not instance.pdf or instance.pdf_miniatura:
        return

    nome, conteudo = _gerar_miniatura(instance.pdf.path, instance.titulo, (230, 390))
    if nome and conteudo:
        instance.pdf_miniatura.save(f'{nome}.jpeg', conteudo, save=False)
        Livro.objects.filter(pk=instance.pk).update(
            pdf_miniatura=instance.pdf_miniatura.name
        )
