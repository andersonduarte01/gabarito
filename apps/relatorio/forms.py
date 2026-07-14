from django import forms

_INPUT = 'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd] dark:[color-scheme:dark]'


class FiltroTurmaPeriodoForm(forms.Form):
    turma          = forms.ModelChoiceField(
        queryset=None, label='Turma',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    periodo_letivo = forms.ModelChoiceField(
        queryset=None, label='Período Letivo',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    formato        = forms.ChoiceField(
        choices=[('html', 'Ver na tela'), ('xlsx', 'Exportar Excel'), ('pdf', 'Exportar PDF')],
        label='Formato',
        widget=forms.Select(attrs={'class': _INPUT}),
    )

    def __init__(self, escola, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.ano_letivo.models import PeriodoLetivo, AnoLetivo, StatusAnoLetivo
        ano_ativo = AnoLetivo.objects.filter(escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO).first()
        qs_turma = Turma.objects.filter(escola=escola, ativo=True)
        if ano_ativo:
            qs_turma = qs_turma.filter(ano_letivo=ano_ativo)
        self.fields['turma'].queryset = qs_turma

        qs_periodo = PeriodoLetivo.objects.none()
        if ano_ativo:
            qs_periodo = PeriodoLetivo.objects.filter(ano_letivo=ano_ativo)
        self.fields['periodo_letivo'].queryset = qs_periodo


class FiltroEscolaPeriodoForm(forms.Form):
    periodo_letivo = forms.ModelChoiceField(
        queryset=None, label='Período Letivo',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    formato        = forms.ChoiceField(
        choices=[('html', 'Ver na tela'), ('xlsx', 'Exportar Excel'), ('pdf', 'Exportar PDF')],
        label='Formato',
        widget=forms.Select(attrs={'class': _INPUT}),
    )

    def __init__(self, escola, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.ano_letivo.models import PeriodoLetivo, AnoLetivo, StatusAnoLetivo
        ano_ativo = AnoLetivo.objects.filter(escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO).first()
        qs_periodo = PeriodoLetivo.objects.filter(ano_letivo=ano_ativo) if ano_ativo else PeriodoLetivo.objects.none()
        self.fields['periodo_letivo'].queryset = qs_periodo


class FiltroBoletimLoteForm(forms.Form):
    turma      = forms.ModelChoiceField(
        queryset=None, label='Turma',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    ano_letivo = forms.ModelChoiceField(
        queryset=None, label='Ano Letivo',
        widget=forms.Select(attrs={'class': _INPUT}),
    )

    def __init__(self, escola, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.ano_letivo.models import AnoLetivo
        self.fields['turma'].queryset = Turma.objects.filter(escola=escola, ativo=True)
        self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(escola=escola).order_by('-ano')


class FiltroFinanceiroForm(forms.Form):
    data_inicio = forms.DateField(
        label='Data inicial',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    data_fim    = forms.DateField(
        label='Data final',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    formato     = forms.ChoiceField(
        choices=[('html', 'Ver na tela'), ('xlsx', 'Exportar Excel'), ('pdf', 'Exportar PDF')],
        label='Formato',
        widget=forms.Select(attrs={'class': _INPUT}),
    )


class FiltroInadimplenciaForm(forms.Form):
    data_inicio = forms.DateField(
        label='Vencimento a partir de', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    data_fim    = forms.DateField(
        label='Vencimento até', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    turma       = forms.ModelChoiceField(
        queryset=None, label='Turma (opcional)', required=False,
        empty_label='Todas as turmas',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    formato     = forms.ChoiceField(
        choices=[('html', 'Ver na tela'), ('xlsx', 'Exportar Excel'), ('pdf', 'Exportar PDF')],
        label='Formato',
        widget=forms.Select(attrs={'class': _INPUT}),
    )

    def __init__(self, escola, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        self.fields['turma'].queryset = Turma.objects.filter(escola=escola, ativo=True)
