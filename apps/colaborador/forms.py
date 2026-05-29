from django import forms

from apps.escola.forms import DaisyFormMixin
from apps.funcao.models import Funcao


class ColaboradorCreateForm(DaisyFormMixin, forms.Form):
    """Formulário de cadastro — cria Usuario + Colaborador via UsuarioService."""

    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        min_length=8,
        help_text='Mínimo 8 caracteres.',
    )
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        required=False,
        help_text='Somente números.',
    )
    telefone = forms.CharField(label='Telefone', max_length=15, required=False)
    funcao = forms.ModelChoiceField(
        label='Função',
        queryset=Funcao.objects.none(),
        required=False,
        empty_label='— Selecione —',
    )
    foto = forms.ImageField(label='Foto', required=False)

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['funcao'].queryset = Funcao.objects.filter(escola=escola)


class ColaboradorEditForm(DaisyFormMixin, forms.Form):
    """Edição dos dados do perfil (não altera senha)."""

    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF', max_length=14, required=False)
    telefone = forms.CharField(label='Telefone', max_length=15, required=False)
    funcao = forms.ModelChoiceField(
        label='Função',
        queryset=Funcao.objects.none(),
        required=False,
        empty_label='— Selecione —',
    )
    foto = forms.ImageField(label='Foto', required=False)

    def __init__(self, *args, escola=None, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['funcao'].queryset = Funcao.objects.filter(escola=escola)
        if instance:
            self.fields['nome'].initial = instance.usuario.nome
            self.fields['email'].initial = instance.usuario.email
            self.fields['cpf'].initial = instance.cpf
            self.fields['telefone'].initial = instance.telefone
            self.fields['funcao'].initial = instance.funcao


class ProfessorCreateForm(DaisyFormMixin, forms.Form):
    """Formulário de cadastro de professor."""

    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        min_length=8,
        help_text='Mínimo 8 caracteres.',
    )
    cpf = forms.CharField(label='CPF', max_length=14, required=False)
    telefone = forms.CharField(label='Telefone', max_length=15, required=False)
    foto = forms.ImageField(label='Foto', required=False)


class ProfessorEditForm(DaisyFormMixin, forms.Form):
    """Edição do perfil do professor."""

    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF', max_length=14, required=False)
    telefone = forms.CharField(label='Telefone', max_length=15, required=False)
    foto = forms.ImageField(label='Foto', required=False)

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['nome'].initial = instance.usuario.nome
            self.fields['email'].initial = instance.usuario.email
            self.fields['cpf'].initial = instance.cpf
            self.fields['telefone'].initial = instance.telefone
