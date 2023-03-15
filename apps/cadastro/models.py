from django.db import models

# Create your models here.

ZONA = [
    ('selecione', 'Selecione'),
    ('Zona Urbana', 'Zona Urbana'),
    ('Zona Rural', 'Zona Rural'),
]


class Cadastro(models.Model):
    nome_escola = models.CharField(verbose_name='Escola', max_length=200)
    inep = models.CharField(verbose_name='INEP', max_length=20)
    email = models.EmailField(verbose_name='Email', max_length=100, unique=True)
    contato = models.CharField(verbose_name='Telefone', max_length=20)
    zona = models.CharField(verbose_name='Zona Urbana/Rural', max_length=100, choices=ZONA, default='selecione')
    rua = models.CharField(verbose_name='Rua', max_length=100)
    numero = models.CharField(verbose_name='Número', max_length=20)
    complemento = models.CharField(verbose_name='Complemento', max_length=200, null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro', max_length=100, null=True, blank=True,
                              help_text='*Em caso de escola da zona rural deixar campo bairro vazio')


    def __str__(self):
        return self.nome_escola


