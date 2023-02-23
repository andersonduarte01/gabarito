from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from pdf2image import convert_from_path

from ..core.models import Usuario
from ..escola.models import UnidadeEscolar
from ..sala.models import Ano


# Create your models here.


class Arquivo(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Titulo')
    escola = models.ForeignKey(Usuario, verbose_name='Autor', on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    pdf = models.FileField(upload_to='arquivos/')
    pdf_miniatura = models.ImageField(upload_to='miniaturas/', blank=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)
    publico = models.BooleanField(verbose_name='Publico', default=True)

    def __str__(self):
        return self.descricao


class Categoria(models.Model):
    categoria = models.CharField(max_length=255, verbose_name='Categoria')

    def __str__(self):
        return self.categoria


class Livro(models.Model):
    titulo = models.CharField(max_length=255, verbose_name='Titulo')
    descricao = models.CharField(max_length=255, verbose_name='Descrição')
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING, verbose_name='Categoria')
    autor = models.CharField(max_length=255, verbose_name='Autor')
    editora = models.CharField(max_length=255, verbose_name='Editora')
    ano_referencia = models.ForeignKey(Ano, on_delete=models.DO_NOTHING , verbose_name='Ano Referência')
    pdf = models.FileField(upload_to='arquivos/')
    pdf_miniatura = models.ImageField(upload_to='miniaturas/', blank=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo



@receiver(post_save, sender=Arquivo)
def update_imagem(sender, instance, **kwargs):
    try:
        if not instance.pdf_miniatura:
            save_dir = r'C:\Users\Anderson\Desktop\projeto\SME\gabarito\media\miniaturas'
            # save_dir = r'/home/anderson/projeto/gabarito/media\miniaturas'
            arquivo = instance.pdf.path
            images_from_path = convert_from_path(arquivo, output_folder=save_dir, fmt='.jpg',
                                                 first_page=0, last_page=1, size=(200, 280))
            blob = open(images_from_path[0].filename, 'rb', encoding='UTF-8')
            fi = blob.read()
            blob.close()
            instance.pdf_miniatura.save(f'{instance.descricao}.jpeg', ContentFile(fi), save=False)
            instance.save()
    except:
        print('Error de formato de documento')


@receiver(post_save, sender=Livro)
def update_imagem(sender, instance, **kwargs):
    try:
        if not instance.pdf_miniatura:
            save_dir = r'C:\Users\Anderson\Desktop\projeto\SME\gabarito\media\miniaturas'
            #save_dir = r'/home/anderson/projeto/gabarito/media\miniaturas'
            livro = instance.pdf.path
            images_from_path = convert_from_path(livro, output_folder=save_dir, fmt='.jpg',
                                                 first_page=0, last_page=1, size=(230, 390))
            blob = open(images_from_path[0].filename, 'rb', encoding='UTF-8')
            fi = blob.read()
            blob.close()
            instance.pdf_miniatura.save(f'{instance.descricao}.jpeg', ContentFile(fi), save=False)
            instance.save()
    except:
        print('Error de formato do livro')
