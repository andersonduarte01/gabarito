from django import forms

from apps.escola.forms import DaisyFormMixin
from apps.sala.models import Sala
from .models import Aluno, SITUACAO, SEXO


class AlunoCreateForm(DaisyFormMixin, forms.Form):
    """
    Criação de aluno — cria Usuario + Aluno via AlunoService.
    """
    nome = forms.CharField(label='Nome completo', max_length=150)
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        required=False,
        help_text='Somente números. Obrigatório para alunos sem responsável.',
    )
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=SEXO,
        initial='M',
    )
    sala = forms.ModelChoiceField(
        label='Sala',
        queryset=Sala.objects.none(),
        required=False,
        empty_label='— Sem sala —',
    )
    responsavel_legal = forms.CharField(
        label='Responsável legal',
        max_length=150,
        required=False,
    )
    tem_responsavel = forms.BooleanField(
        label='Possui responsável?',
        required=False,
        initial=True,
        help_text='Alunos com responsável não têm acesso ao sistema.',
    )
    email = forms.EmailField(
        label='E-mail do aluno',
        required=False,
        help_text='Obrigatório apenas para alunos sem responsável.',
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        required=False,
        min_length=8,
        help_text='Obrigatório apenas para alunos sem responsável.',
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['sala'].queryset = (
                Sala.objects.filter(escola=escola).select_related('ano', 'ano_letivo')
            )

    def clean(self):
        cleaned = super().clean()
        tem_responsavel = cleaned.get('tem_responsavel', True)
        if not tem_responsavel:
            if not cleaned.get('email'):
                self.add_error('email', 'E-mail é obrigatório para alunos sem responsável.')
            if not cleaned.get('password'):
                self.add_error('password', 'Senha é obrigatória para alunos sem responsável.')
            if not cleaned.get('cpf'):
                self.add_error('cpf', 'CPF é obrigatório para alunos sem responsável.')
        return cleaned


class AlunoEditForm(DaisyFormMixin, forms.ModelForm):
    """Edição do perfil do aluno (não altera usuario/email)."""

    class Meta:
        model = Aluno
        fields = ('sala', 'data_nascimento', 'sexo', 'responsavel_legal', 'situacao')
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['sala'].queryset = (
                Sala.objects.filter(escola=escola).select_related('ano', 'ano_letivo')
            )
        self.fields['sala'].required = False
        self.fields['sala'].empty_label = '— Sem sala —'
