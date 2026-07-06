from django import forms

from .models import Parentesco, PerfilResponsavel, VinculoResponsavelAluno

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
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
_CHECK = 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'


class CriarResponsavelForm(forms.Form):
    """Responsável com acesso ao sistema."""
    foto            = forms.ImageField(
        label='Foto', required=False,
        widget=forms.FileInput(attrs={'class': _FILE}),
    )
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
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
    )
    email           = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@exemplo.com'}),
    )
    senha           = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Senha de acesso'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Repita a senha'}),
    )
    # vínculo com aluno (opcional)
    aluno                  = forms.ModelChoiceField(
        label='Vincular a aluno', queryset=None, required=False, empty_label='— Nenhum —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    parentesco             = forms.ChoiceField(
        label='Parentesco', choices=[('', '— Selecione —')] + list(Parentesco.choices), required=False,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    responsavel_principal  = forms.BooleanField(
        label='Responsável principal', required=False,
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
    )
    responsavel_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
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

    def clean(self):
        cleaned = super().clean()
        s1 = cleaned.get('senha')
        s2 = cleaned.get('confirmar_senha')
        if s1 and s2 and s1 != s2:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        if cleaned.get('aluno') and not cleaned.get('parentesco'):
            self.add_error('parentesco', 'Informe o parentesco ao vincular um aluno.')
        return cleaned


class CriarSemAcessoForm(forms.Form):
    """Responsável sem login — apenas contato."""
    foto            = forms.ImageField(
        label='Foto', required=False,
        widget=forms.FileInput(attrs={'class': _FILE}),
    )
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
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
    )
    # vínculo com aluno (opcional)
    aluno                  = forms.ModelChoiceField(
        label='Vincular a aluno', queryset=None, required=False, empty_label='— Nenhum —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    parentesco             = forms.ChoiceField(
        label='Parentesco', choices=[('', '— Selecione —')] + list(Parentesco.choices), required=False,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    responsavel_principal  = forms.BooleanField(
        label='Responsável principal', required=False,
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
    )
    responsavel_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
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

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('aluno') and not cleaned.get('parentesco'):
            self.add_error('parentesco', 'Informe o parentesco ao vincular um aluno.')
        return cleaned


class EditarResponsavelForm(forms.ModelForm):
    class Meta:
        model   = PerfilResponsavel
        fields  = ('foto', 'nome', 'telefone', 'cpf', 'rg', 'data_nascimento')
        widgets = {
            'foto':            forms.FileInput(attrs={'class': _FILE}),
            'nome':            forms.TextInput(attrs={'class': _INPUT}),
            'telefone':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
            'cpf':             forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'rg':              forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
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
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
    )
    responsavel_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': _CHECK}),
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
