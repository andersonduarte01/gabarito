from django.conf import settings
from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano


class Categoria(models.Model):
    titulo = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)
            slug, n = base, 1
            while Categoria.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class Blog(models.Model):
    titulo = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to='Imagens/Noticias', null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Autor', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True)
    conteudo = RichTextUploadingField()
    data = models.DateField(auto_now_add=True)
    data_atualizacao = models.DateField(auto_now=True)
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)
            slug, n = base, 1
            while Blog.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'

    def imagem00(self):
        return bool(self.imagem)


class Video(models.Model):
    numero = models.CharField(max_length=255, verbose_name='Numero', default='')
    titulo = models.CharField(max_length=255, verbose_name='Título')
    url_video = models.CharField(max_length=255, verbose_name='Url')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING, null=True, blank=True)
    materia = models.CharField(verbose_name='Materia', max_length=255, null=True, blank=True)
    sigla = models.CharField(verbose_name='Sigla', max_length=255, null=True, blank=True)
    professora = models.CharField(verbose_name='Professor(a)', max_length=255, null=True, blank=True)
    tempo = models.CharField(verbose_name='Tempo', max_length=255, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    data_atualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

