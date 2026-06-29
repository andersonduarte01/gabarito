from django import forms

from apps.core.models import Endereco

from .models import CargoDiretor, PerfilDiretor

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


class EditarPerfilDiretorForm(forms.ModelForm):
    nome = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT}),
    )

    class Meta:
        model  = PerfilDiretor
        fields = ['cargo', 'cpf', 'data_nascimento', 'telefone',
                  'numero_ato', 'data_ato', 'data_inicio']
        widgets = {
            'cargo':           forms.Select(attrs={'class': _SELECT}),
            'cpf':             forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'telefone':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
            'numero_ato':      forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nº do ato de nomeação'}),
            'data_ato':        forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'data_inicio':     forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['nome'].initial  = usuario.nome
            self.fields['email'].initial = usuario.email


class CriarDiretorForm(forms.Form):
    nome            = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    email           = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@escola.com.br'}),
    )
    cargo           = forms.ChoiceField(
        choices=CargoDiretor.choices, label='Cargo',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    cpf             = forms.CharField(
        max_length=14, required=False, label='CPF',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    telefone        = forms.CharField(
        max_length=20, required=False, label='Telefone',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    data_nascimento = forms.DateField(
        required=False, label='Data de Nascimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    data_inicio     = forms.DateField(
        required=False, label='Data de Início no Cargo',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )


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
