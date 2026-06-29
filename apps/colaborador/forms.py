from django import forms

from apps.core.models import Endereco
from .models import FuncaoEscolar, PerfilColaborador, TipoVinculoEmpregaticio

_ESTADOS_BR = [
    ('', 'Selecione'),
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
    ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
    ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'),
    ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT = _INPUT


class CriarColaboradorForm(forms.Form):
    nome            = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    email           = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@escola.com.br'}),
    )
    funcao          = forms.ModelChoiceField(
        queryset=FuncaoEscolar.objects.none(),
        required=False, label='Função',
        widget=forms.Select(attrs={'class': _SELECT}),
        empty_label='(sem função)',
    )
    tipo_vinculo    = forms.ChoiceField(
        choices=TipoVinculoEmpregaticio.choices, label='Tipo de Vínculo',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    cpf             = forms.CharField(
        max_length=14, required=False, label='CPF',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    rg              = forms.CharField(
        max_length=20, required=False, label='RG',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    data_nascimento = forms.DateField(
        required=False, label='Data de Nascimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    telefone        = forms.CharField(
        max_length=20, required=False, label='Telefone',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    data_admissao   = forms.DateField(
        required=False, label='Data de Admissão',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    pis             = forms.CharField(
        max_length=20, required=False, label='PIS/PASEP',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola is not None:
            self.fields['funcao'].queryset = FuncaoEscolar.objects.filter(escola=escola, ativo=True)


class EditarColaboradorForm(forms.ModelForm):
    nome  = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT}),
    )

    class Meta:
        model  = PerfilColaborador
        fields = ['funcao', 'tipo_vinculo', 'cpf', 'rg',
                  'data_nascimento', 'telefone', 'data_admissao', 'pis']
        widgets = {
            'funcao':          forms.Select(attrs={'class': _SELECT}),
            'tipo_vinculo':    forms.Select(attrs={'class': _SELECT}),
            'cpf':             forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'rg':              forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'telefone':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
            'data_admissao':   forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'pis':             forms.TextInput(attrs={'class': _INPUT}),
        }

    def __init__(self, *args, escola=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola is not None:
            self.fields['funcao'].queryset = FuncaoEscolar.objects.filter(escola=escola, ativo=True)
            self.fields['funcao'].empty_label = '(sem função)'
            self.fields['funcao'].required = False
        if usuario is not None:
            self.fields['nome'].initial  = usuario.nome
            self.fields['email'].initial = usuario.email


class EnderecoPerfilForm(forms.ModelForm):
    uf = forms.ChoiceField(
        choices=_ESTADOS_BR,
        widget=forms.Select(attrs={'class': _SELECT}),
        label='UF',
    )

    class Meta:
        model  = Endereco
        fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'municipio', 'uf']
        widgets = {
            'cep':         forms.TextInput(attrs={'class': _INPUT, 'placeholder': '00000-000'}),
            'logradouro':  forms.TextInput(attrs={'class': _INPUT}),
            'numero':      forms.TextInput(attrs={'class': _INPUT}),
            'complemento': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Opcional'}),
            'bairro':      forms.TextInput(attrs={'class': _INPUT}),
            'municipio':   forms.TextInput(attrs={'class': _INPUT}),
        }


class FuncaoEscolarForm(forms.Form):
    nome = forms.CharField(
        max_length=100, label='Nome da Função',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Secretária, Coordenador Pedagógico'}),
    )
