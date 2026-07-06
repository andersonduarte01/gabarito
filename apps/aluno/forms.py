from django import forms

from .models import Aluno

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


class CriarAlunoForm(forms.Form):
    foto            = forms.ImageField(
        label='Foto', required=False,
        widget=forms.FileInput(attrs={'class': _FILE}),
    )
    nome_completo   = forms.CharField(
        label='Nome Completo', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo do aluno'}),
    )
    data_nascimento = forms.DateField(
        label='Data de Nascimento', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
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
    # ── Responsável (opcional) ──────────────────────────────────────────────
    resp_nome       = forms.CharField(
        label='Nome do Responsável', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Nome completo'}),
    )
    resp_telefone   = forms.CharField(
        label='Telefone', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 00000-0000'}),
    )
    resp_cpf        = forms.CharField(
        label='CPF', max_length=14, required=False,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': '000.000.000-00'}),
    )
    resp_parentesco = forms.ChoiceField(
        label='Parentesco', required=False,
        choices=[('', '— Selecione —')],
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    resp_principal  = forms.BooleanField(
        label='Responsável principal', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )
    resp_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.ano_letivo.models import AnoLetivo
        from apps.responsavel.models import Parentesco
        if escola:
            self.fields['turma'].queryset      = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
        else:
            self.fields['turma'].queryset      = Turma.objects.none()
            self.fields['ano_letivo'].queryset = Turma.objects.none()
        self.fields['resp_parentesco'].choices = [('', '— Selecione —')] + list(Parentesco.choices)

    def clean(self):
        cleaned    = super().clean()
        turma      = cleaned.get('turma')
        ano_letivo = cleaned.get('ano_letivo')
        if turma and not ano_letivo:
            self.add_error('ano_letivo', 'Selecione o ano letivo ao vincular uma turma.')
        if ano_letivo and not turma:
            self.add_error('turma', 'Selecione a turma para o ano letivo informado.')
        if cleaned.get('resp_nome') and not cleaned.get('resp_parentesco'):
            self.add_error('resp_parentesco', 'Informe o parentesco do responsável.')
        return cleaned


class EditarAlunoForm(forms.ModelForm):
    class Meta:
        model  = Aluno
        fields = ('foto', 'nome_completo', 'data_nascimento', 'cpf', 'rg')
        widgets = {
            'foto':            forms.FileInput(attrs={'class': _FILE}),
            'nome_completo':   forms.TextInput(attrs={'class': _INPUT}),
            'data_nascimento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
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


class AtivarAcessoForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': _INPUT, 'placeholder': 'email@exemplo.com'}),
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Senha de acesso'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': _INPUT, 'placeholder': 'Repita a senha'}),
    )

    def clean(self):
        cleaned = super().clean()
        s1 = cleaned.get('senha')
        s2 = cleaned.get('confirmar_senha')
        if s1 and s2 and s1 != s2:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned


class VincularResponsavelForm(forms.Form):
    responsavel = forms.ModelChoiceField(
        label='Responsável', queryset=None, empty_label='— Selecione —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    parentesco = forms.ChoiceField(
        label='Parentesco', choices=[],
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    responsavel_principal = forms.BooleanField(
        label='Responsável principal', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )
    responsavel_financeiro = forms.BooleanField(
        label='Responsável financeiro', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        from apps.responsavel.models import Parentesco, PerfilResponsavel
        self.fields['parentesco'].choices = Parentesco.choices
        if escola:
            self.fields['responsavel'].queryset = (
                PerfilResponsavel.objects
                .filter(Q(escola=escola) | Q(vinculos_aluno__aluno__escola=escola))
                .distinct()
                .order_by('nome')
            )
        else:
            self.fields['responsavel'].queryset = PerfilResponsavel.objects.none()


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
