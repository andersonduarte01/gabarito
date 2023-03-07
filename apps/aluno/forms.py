from django import forms
from django.conf import settings
from ..aluno.models import Aluno
from ..perfil.models import Pessoa, Endereco
from ..sala.models import Sala
from datetime import datetime


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ('nome', 'sala')

    def __init__(self, *args, **kwargs):
        escola = kwargs.pop('escola')
        super(AlunoForm, self).__init__(*args, **kwargs)
        self.fields['sala'].queryset = Sala.objects.filter(escola=escola)


class EditarAlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ('nome', 'sala', 'data_nascimento', 'sexo',  'portador_deficiencia', 'situacao', 'responsavel_legal')

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(EditarAlunoForm, self).__init__(*args, **kwargs)
        if instance:
            self.instance = instance
            self.fields['sala'].initial = instance.sala
            self.fields['nome'].initial = instance
            self.fields['data_nascimento'].initial = instance.data_nascimento.strftime("%d/%m/%Y")
            self.fields['sexo'].initial = instance.sexo
            self.fields['portador_deficiencia'].initial = instance.portador_deficiencia
            self.fields['situacao'].initial = instance.situacao
            self.fields['responsavel_legal'].initial = instance.responsavel_legal
            self.fields['sala'].queryset = Sala.objects.filter(escola=instance.sala.escola)


class PessoaForm(forms.ModelForm):
    data_nascimento = forms.DateTimeField(input_formats=settings.DATE_INPUT_FORMATS)
    class Meta:
        model = Pessoa
        fields = ('cpf', 'data_nascimento', 'telefone')

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(PessoaForm, self).__init__(*args, **kwargs)
        if instance:
            self.instance = instance
            self.fields['cpf'].initial = instance.cpf
            self.fields['data_nascimento'].initial = instance.data_nascimento.strftime("%d/%m/%Y")
            self.fields['telefone'].initial = instance.telefone


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ('rua', 'numero', 'complemento', 'bairro')

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(EnderecoForm, self).__init__(*args, **kwargs)
        if instance:
            self.instance = instance
            self.fields['rua'].initial = instance.rua
            self.fields['numero'].initial = instance.numero
            self.fields['complemento'].initial = instance.complemento
            self.fields['bairro'].initial = instance.bairro

