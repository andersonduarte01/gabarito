from django import forms

from .models import Aluno

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT = _INPUT


class CriarAlunoForm(forms.Form):
    nome_completo   = forms.CharField(
        label='Nome Completo', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo do aluno'}),
    )
    data_nascimento = forms.DateField(
        label='Data de Nascimento', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    cpf             = forms.CharField(
        label='CPF', max_length=14, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    rg              = forms.CharField(
        label='RG', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    turma           = forms.ModelChoiceField(
        label='Turma', queryset=None, required=False, empty_label='— Sem turma —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    ano_letivo      = forms.ModelChoiceField(
        label='Ano Letivo', queryset=None, required=False, empty_label='— Selecione —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.ano_letivo.models import AnoLetivo
        if escola:
            self.fields['turma'].queryset      = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
        else:
            self.fields['turma'].queryset      = Turma.objects.none()
            self.fields['ano_letivo'].queryset = Turma.objects.none()

    def clean(self):
        cleaned    = super().clean()
        turma      = cleaned.get('turma')
        ano_letivo = cleaned.get('ano_letivo')
        if turma and not ano_letivo:
            self.add_error('ano_letivo', 'Selecione o ano letivo ao vincular uma turma.')
        if ano_letivo and not turma:
            self.add_error('turma', 'Selecione a turma para o ano letivo informado.')
        return cleaned


class EditarAlunoForm(forms.ModelForm):
    class Meta:
        model  = Aluno
        fields = ('nome_completo', 'data_nascimento', 'cpf', 'rg')
        widgets = {
            'nome_completo':   forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'cpf':             forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
            'rg':              forms.TextInput(attrs={'class': _INPUT}),
        }


class MatriculaTurmaForm(forms.Form):
    turma      = forms.ModelChoiceField(
        label='Turma', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    ano_letivo = forms.ModelChoiceField(
        label='Ano Letivo', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.ano_letivo.models import AnoLetivo
        if escola:
            self.fields['turma'].queryset      = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
        else:
            self.fields['turma'].queryset      = Turma.objects.none()
            self.fields['ano_letivo'].queryset = Turma.objects.none()


class TrocarTurmaForm(forms.Form):
    nova_turma = forms.ModelChoiceField(
        label='Nova Turma', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        if escola:
            self.fields['nova_turma'].queryset = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
        else:
            self.fields['nova_turma'].queryset = Turma.objects.none()
