from decimal import Decimal

from django import forms

from .models import GatewayCobranca, Periodicidade, PlanoFinanceiro

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT   = _INPUT
_TEXTAREA = _INPUT + ' resize-none'


class PlanoFinanceiroForm(forms.ModelForm):
    class Meta:
        model  = PlanoFinanceiro
        fields = ('nome', 'descricao', 'valor', 'periodicidade', 'ativo')
        widgets = {
            'nome':          forms.TextInput(attrs={'class': _INPUT}),
            'descricao':     forms.Textarea(attrs={'class': _TEXTAREA, 'rows': 3}),
            'valor':         forms.NumberInput(attrs={'class': _INPUT, 'step': '0.01', 'min': '0'}),
            'periodicidade': forms.Select(attrs={'class': _SELECT}),
            'ativo':         forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
        }

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._escola = escola


class CobrancaAlunoForm(forms.Form):
    descricao         = forms.CharField(
        label='Descrição', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Mensalidade Julho/2026'}),
    )
    valor             = forms.DecimalField(
        label='Valor (R$)', max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': _INPUT, 'step': '0.01', 'min': '0'}),
    )
    vencimento        = forms.DateField(
        label='Vencimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    plano_financeiro  = forms.ModelChoiceField(
        label='Plano', queryset=PlanoFinanceiro.objects.none(),
        required=False, empty_label='— Avulso (sem plano) —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    gateway           = forms.ChoiceField(
        label='Gateway', choices=GatewayCobranca.choices,
        widget=forms.Select(attrs={'class': _SELECT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['plano_financeiro'].queryset = (
                PlanoFinanceiro.objects.filter(escola=escola, ativo=True).order_by('nome')
            )


class GerarCobrancasTurmaForm(forms.Form):
    plano_financeiro = forms.ModelChoiceField(
        label='Plano', queryset=PlanoFinanceiro.objects.none(),
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    vencimento       = forms.DateField(
        label='Vencimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    turma            = forms.ModelChoiceField(
        label='Turma', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        if escola:
            self.fields['plano_financeiro'].queryset = (
                PlanoFinanceiro.objects.filter(escola=escola, ativo=True).order_by('nome')
            )
            self.fields['turma'].queryset = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
        else:
            from apps.turma.models import Turma
            self.fields['turma'].queryset = Turma.objects.none()


class GerarCobrancasEscolaForm(forms.Form):
    plano_financeiro = forms.ModelChoiceField(
        label='Plano', queryset=PlanoFinanceiro.objects.none(),
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    vencimento       = forms.DateField(
        label='Vencimento',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['plano_financeiro'].queryset = (
                PlanoFinanceiro.objects.filter(escola=escola, ativo=True).order_by('nome')
            )
