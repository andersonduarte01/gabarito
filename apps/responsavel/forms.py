from django import forms

from .models import Parentesco, PerfilResponsavel, VinculoResponsavelAluno

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT = _INPUT


class CriarResponsavelForm(forms.Form):
    """Responsável com acesso ao sistema."""
    nome            = forms.CharField(
        label='Nome Completo', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    email           = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@exemplo.com'}),
    )
    telefone        = forms.CharField(
        label='Telefone', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    cpf             = forms.CharField(
        label='CPF', max_length=14, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    rg              = forms.CharField(
        label='RG', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    data_nascimento = forms.DateField(
        label='Data de Nascimento', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )


class CriarSemAcessoForm(forms.Form):
    """Responsável sem login — apenas contato."""
    nome            = forms.CharField(
        label='Nome Completo', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    telefone        = forms.CharField(
        label='Telefone', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    cpf             = forms.CharField(
        label='CPF', max_length=14, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    rg              = forms.CharField(
        label='RG', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    data_nascimento = forms.DateField(
        label='Data de Nascimento', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )


class EditarResponsavelForm(forms.ModelForm):
    class Meta:
        model   = PerfilResponsavel
        fields  = ('nome', 'telefone', 'cpf', 'rg', 'data_nascimento')
        widgets = {
            'nome':            forms.TextInput(attrs={'class': _INPUT}),
            'telefone':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
            'cpf':             forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'rg':              forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
        }


class VincularAlunoForm(forms.Form):
    aluno                  = forms.ModelChoiceField(
        label='Aluno', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    parentesco             = forms.ChoiceField(
        label='Parentesco', choices=Parentesco.choices,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    responsavel_principal  = forms.BooleanField(
        label='Responsável principal', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )
    responsavel_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.aluno.models import Aluno
        if escola:
            self.fields['aluno'].queryset = (
                Aluno.objects.filter(escola=escola, ativo=True).order_by('nome_completo')
            )
        else:
            self.fields['aluno'].queryset = Aluno.objects.none()
