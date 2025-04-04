import os
import uuid

from cpf_field.models import CPFField
from django.db import models
from stdimage import StdImageField

from .validador import validate_pdf_extension
from ..core.models import Usuario
from ..escola.models import UnidadeEscolar

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
    rua = models.CharField(verbose_name='Rua/Sitio', max_length=100)
    numero = models.CharField(verbose_name='Número', max_length=20)
    complemento = models.CharField(verbose_name='Complemento', max_length=200, null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro', max_length=100, null=True, blank=True,
                              help_text='*Em caso de escola da zona rural deixar campo bairro vazio')


    def __str__(self):
        return self.nome_escola


class Cargo(models.Model):
    funcao = models.CharField(max_length=200, verbose_name='Funcao')

    def __str__(self):
        return self.funcao

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

class CadastroInicio(Usuario):
    cpf = CPFField('CPF')


def arquivo_foto(instance, filename):
    if filename:
        ext = filename.split('.')[-1]  # Obtém a extensão do arquivo original
        random_name = str(uuid.uuid4())  # Gera um nome aleatório
        new_filename = f"{random_name}.{ext}"  # Cria o novo nome do arquivo
        return os.path.join('Imagens/perfil', new_filename)
    return filename  # Retorna o nome original se for None


class RG(models.Model):
    rg_cnh = models.FileField(upload_to='docs/rg', verbose_name='Anexar RG/CNH',
                             help_text='Anexar arquivo em formato PDF',
                             max_length=300, validators=[validate_pdf_extension])
    cpf = models.FileField(upload_to='docs/rg', verbose_name='Anexar CPF',
                              help_text='Anexar arquivo em formato PDF',
                              max_length=300, validators=[validate_pdf_extension])
    numero = models.CharField(verbose_name='Numero', max_length=30)
    emissao = models.CharField(verbose_name='Data de Emissão', max_length=10, help_text='dd/mm/aaaa')
    status_rg = models.BooleanField(default=False)

    def __str__(self):
        return self.numero


class Endereco(models.Model):
    ZONA = [
        ('Zona Urbana', 'Zona Urbana'),
        ('Zona Rural', 'Zona Rural'),
    ]
    comprovate = models.FileField(upload_to='docs/comprovante', verbose_name='Comprovante de endereco',
                             help_text='Anexar arquivo em formato PDF',
                             max_length=300, validators=[validate_pdf_extension])
    rua = models.CharField(verbose_name='Rua', max_length=100, null=True, blank=True)
    numero = models.CharField(verbose_name='Número', max_length=15, null=True, blank=True)
    bairro = models.CharField(verbose_name='Bairro', max_length=150, null=True, blank=True)
    complemento = models.CharField(verbose_name='Complemento', max_length=250, null=True, blank=True)
    area = models.CharField(verbose_name='Área', choices=ZONA, max_length=30)
    localidade_sitio = models.CharField(verbose_name='Localidade/Sítio', max_length=150, null=True, blank=True)
    status_endereco = models.BooleanField(default=False)

    def __str__(self):
        return self.complemento


class Profissional(models.Model):
    FUNCAO = [
        ('selecione', 'Selecione'),
        ('Concursado', 'Concursado'),
        ('Contratado', 'Contratado'),
        ('Comissionado', 'Comissionado'),
    ]
    nomeacao = models.FileField(upload_to='docs/nomeacao1', verbose_name='Anexar arquivo', null=True, blank=True,
                             help_text='Anexar arquivo em formato PDF',
                             max_length=300, validators=[validate_pdf_extension])
    vinculo = models.CharField(verbose_name='Vínculo', max_length=100, choices=FUNCAO)
    funcao = models.ForeignKey(Cargo, max_length=100, null=True, blank=True, on_delete=models.DO_NOTHING)
    lotado = models.ForeignKey(UnidadeEscolar, verbose_name='Lotado', max_length=250, on_delete=models.DO_NOTHING)
    data_admissao = models.CharField(verbose_name='Data Admissão', max_length=50, help_text='dd/mm/aaaa')
    experiencia = models.TextField(verbose_name='Experiência', help_text='Breve descrição de trabalhos anteriores', null=True, blank=True)
    status_profisssional = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.vinculo} - {self.funcao} ({self.lotado})'


class CadUnificado(models.Model):
    SEXO = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino')
    ]
    foto = StdImageField(upload_to=arquivo_foto,
                         variations={'thumbnail': {'width': 600, 'height': 800}})
    usuario = models.ForeignKey(CadastroInicio, on_delete=models.CASCADE)
    data_nascimento = models.CharField(verbose_name='Data de Nascimento', null=True, blank=True, help_text='dd/mm/aaaa', max_length=12)
    sexo = models.CharField(verbose_name='Sexo', max_length=20, choices=SEXO)
    telefone = models.CharField(verbose_name='Telefone', max_length=20, null=True, blank=True, help_text='(88) 9 8888 8888')
    rg_cnh = models.ForeignKey(RG, verbose_name='RG/CNH', max_length=250, on_delete=models.DO_NOTHING, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, verbose_name='Endereço', max_length=250, on_delete=models.DO_NOTHING, null=True, blank=True)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', max_length=250, on_delete=models.DO_NOTHING, null=True, blank=True)
    status_unico = models.BooleanField(default=False)

    def __str__(self):
        return self.telefone

    class Meta:
        unique_together = [
            ('usuario', 'rg_cnh'),
            ('usuario', 'endereco'),
            ('usuario', 'profissional'),
        ]

    def imagem(self):
        if self.foto:
            return True
        else:
            return False

    class Meta:
        verbose_name = 'Cad. Unificado'
        verbose_name_plural = 'Cad. Unificados'
