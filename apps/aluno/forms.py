from django import forms

from apps.escola.forms import DaisyFormMixin
from apps.sala.models import Turma
from .models import Aluno, SEXO, SITUACAO


class AlunoCreateForm(DaisyFormMixin, forms.Form):
    # ── Dados pessoais ────────────────────────────────────────────────────────
    nome = forms.CharField(label='Nome completo', max_length=150)
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    sexo = forms.ChoiceField(label='Sexo', choices=SEXO, required=False)
    cpf = forms.CharField(label='CPF', max_length=14, required=False)
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)

    # ── Responsável ───────────────────────────────────────────────────────────
    tem_responsavel = forms.BooleanField(
        label='Possui responsável',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'toggle toggle-primary',
            'role': 'switch',
        }),
    )
    responsavel_legal = forms.CharField(
        label='Nome do responsável', max_length=150, required=False,
    )
    telefone_responsavel = forms.CharField(
        label='Telefone do responsável', max_length=20, required=False,
    )

    # ── Vínculo escolar ───────────────────────────────────────────────────────
    sala = forms.ModelChoiceField(
        label='Turma',
        queryset=Turma.objects.none(),
        required=False,
        empty_label='— Sem turma —',
    )

    # ── Acesso ao sistema ─────────────────────────────────────────────────────
    email = forms.EmailField(label='E-mail de acesso')
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(render_value=False),
        min_length=8,
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['sala'].queryset = (
                Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('tem_responsavel'):
            cleaned['responsavel_legal'] = ''
            cleaned['telefone_responsavel'] = ''
        return cleaned


class AlunoEditForm(DaisyFormMixin, forms.ModelForm):
    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail de acesso', required=False)
    tem_responsavel = forms.BooleanField(
        label='Possui responsável',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'toggle toggle-primary',
            'role': 'switch',
        }),
    )

    class Meta:
        model = Aluno
        fields = (
            'cpf', 'data_nascimento', 'sexo',
            'telefone', 'responsavel_legal', 'telefone_responsavel',
            'sala', 'situacao',
        )
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d',
            ),
        }

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['nome'].initial = self.instance.usuario.nome
            self.fields['email'].initial = self.instance.usuario.email
            self.fields['tem_responsavel'].initial = bool(self.instance.responsavel_legal)
        if escola:
            self.fields['sala'].queryset = (
                Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            )
        else:
            self.fields['sala'].queryset = Turma.objects.none()
        self.fields['sala'].required = False
        self.fields['sala'].empty_label = '— Sem turma —'
        self.fields['cpf'].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('tem_responsavel'):
            cleaned['responsavel_legal'] = ''
            cleaned['telefone_responsavel'] = ''
        return cleaned
