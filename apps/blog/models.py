from django.db import models
from tinymce.models import HTMLField

# Create your models here.
from ..escola.models import UnidadeEscolar


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
    conteudo = HTMLField()
    data = models.DateField(auto_now_add=True)
    data_atualizacao = models.DateField(auto_now=True)
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'


