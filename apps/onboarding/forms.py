from django import forms

from apps.diretor.models import CargoDiretor
from apps.escola.models import TipoInstituicao
from apps.onboarding.models import CanalConvite

INPUT    = 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors'
SELECT   = INPUT
PASSWORD = INPUT + ' pr-12'


class CriarEscolaForm(forms.Form):
    nome_escola       = forms.CharField(
        label='Nome da Escola',
        max_length=200,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nome completo da instituição'}),
    )
    cnpj              = forms.CharField(
        label='CNPJ',
        max_length=18,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': '00.000.000/0000-00'}),
    )
    tipo              = forms.ChoiceField(
        label='Tipo de Instituição',
        choices=TipoInstituicao.choices,
        initial=TipoInstituicao.PRIVADA,
        widget=forms.Select(attrs={'class': SELECT}),
    )
    nome_diretor      = forms.CharField(
        label='Nome do Diretor',
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nome completo'}),
    )
    email_diretor     = forms.EmailField(
        label='E-mail do Diretor',
        widget=forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'diretor@escola.com.br'}),
    )
    telefone_diretor  = forms.CharField(
        label='Telefone do Diretor',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': '(83) 99999-9999'}),
    )
    canal_envio       = forms.ChoiceField(
        label='Canal de Envio do Convite',
        choices=CanalConvite.choices,
        initial=CanalConvite.EMAIL,
        widget=forms.Select(attrs={'class': SELECT}),
    )


class CompletarCadastroForm(forms.Form):
    senha            = forms.CharField(
        label='Nova Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': PASSWORD, 'placeholder': 'Mínimo 8 caracteres'}),
    )
    confirmar_senha  = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': PASSWORD, 'placeholder': 'Repita a senha'}),
    )
    cargo            = forms.ChoiceField(
        label='Cargo',
        choices=CargoDiretor.choices,
        initial=CargoDiretor.TITULAR,
        widget=forms.Select(attrs={'class': SELECT}),
    )
    cpf              = forms.CharField(
        label='CPF',
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': '000.000.000-00'}),
    )
    data_nascimento  = forms.DateField(
        label='Data de Nascimento',
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
    )
    telefone         = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': '(83) 99999-9999'}),
    )
    data_inicio      = forms.DateField(
        label='Data de Início no Cargo',
        required=False,
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
    )

    def clean(self):
        cleaned = super().clean()
        senha   = cleaned.get('senha')
        confirm = cleaned.get('confirmar_senha')
        if senha and confirm and senha != confirm:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        return cleaned
