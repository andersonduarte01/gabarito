from django import forms

from apps.core.models import Endereco
from .models import FormacaoAcademica, NivelFormacao, PerfilProfessor, TipoVinculoProfessor

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd] '
    'dark:[color-scheme:dark]'
)
_SELECT = _INPUT
_FILE = (
    'w-full text-sm text-slate-600 dark:text-slate-400 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'bg-white dark:bg-slate-800 cursor-pointer '
    'file:cursor-pointer file:border-0 file:mr-3 file:px-4 file:py-2 '
    'file:text-sm file:font-medium '
    'file:bg-slate-100 file:text-slate-600 '
    'dark:file:bg-slate-700 dark:file:text-slate-300 '
    'file:hover:bg-slate-200 dark:file:hover:bg-slate-600 '
    'file:transition-colors'
)

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


class CriarProfessorForm(forms.Form):
    foto                  = forms.ImageField(
        required=False, label='Foto',
        widget=forms.FileInput(attrs={'class': _FILE}),
    )
    nome                  = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    email                 = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@escola.com.br'}),
    )
    tipo_vinculo          = forms.ChoiceField(
        choices=TipoVinculoProfessor.choices, label='Tipo de Vínculo',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    registro_profissional = forms.CharField(
        max_length=50, required=False, label='Registro Profissional',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: CREF, CRP...'}),
    )
    cpf                   = forms.CharField(
        max_length=14, required=False, label='CPF',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    rg                    = forms.CharField(
        max_length=20, required=False, label='RG',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    data_nascimento       = forms.DateField(
        required=False, label='Data de Nascimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
    )
    telefone              = forms.CharField(
        max_length=20, required=False, label='Telefone',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    data_admissao         = forms.DateField(
        required=False, label='Data de Admissão',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
    )
    senha                 = forms.CharField(
        label='Senha', min_length=8,
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Mínimo 8 caracteres'}),
    )
    confirmar_senha       = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Repita a senha'}),
    )

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned


class EditarProfessorForm(forms.ModelForm):
    nome  = forms.CharField(
        max_length=150, label='Nome completo',
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT}),
    )

    class Meta:
        model  = PerfilProfessor
        fields = ['foto', 'tipo_vinculo', 'registro_profissional', 'cpf', 'rg',
                  'data_nascimento', 'telefone', 'data_admissao']
        widgets = {
            'foto':                  forms.FileInput(attrs={'class': _FILE}),
            'tipo_vinculo':          forms.Select(attrs={'class': _SELECT}),
            'registro_profissional': forms.TextInput(attrs={'class': _INPUT}),
            'cpf':                   forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'rg':                    forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento':       forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
            'telefone':              forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
            'data_admissao':         forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['nome'].initial  = usuario.nome
            self.fields['email'].initial = usuario.email


class AlterarSenhaProfessorForm(forms.Form):
    nova_senha      = forms.CharField(
        label='Nova senha', min_length=8,
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Mínimo 8 caracteres'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Repita a nova senha'}),
    )

    def clean(self):
        cleaned = super().clean()
        nova = cleaned.get('nova_senha')
        confirmar = cleaned.get('confirmar_senha')
        if nova and confirmar and nova != confirmar:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned


class FormacaoAcademicaForm(forms.ModelForm):
    class Meta:
        model  = FormacaoAcademica
        fields = ['nivel', 'curso', 'instituicao', 'ano_conclusao']
        widgets = {
            'nivel':         forms.Select(attrs={'class': _SELECT}),
            'curso':         forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Licenciatura em Matemática'}),
            'instituicao':   forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome da instituição'}),
            'ano_conclusao': forms.NumberInput(attrs={'class': _INPUT, 'placeholder': 'Ex: 2015', 'min': 1950, 'max': 2099}),
        }


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
