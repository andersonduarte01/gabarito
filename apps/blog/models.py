from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano


class Categoria(models.Model):
    titulo = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class Blog(models.Model):
    titulo = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to='Imagens/Noticias', null=True, blank=True)
    autor = models.ForeignKey(UnidadeEscolar, verbose_name='Autor', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200)
    conteudo = RichTextField()
    data = models.DateField(auto_now_add=True)
    data_atualizacao = models.DateField(auto_now=True)
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'

    def imagem00(self):
        if self.imagem:
            return True
        else:
            return False


class Video(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Título')
    url_video = models.CharField(max_length=255, verbose_name='Url')
    ano = models.ForeignKey(Ano, on_delete=models.DO_NOTHING, null=True, blank=True)
    materia = models.CharField(verbose_name='Materia', max_length=255, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    data_atualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

