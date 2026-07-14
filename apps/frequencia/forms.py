from django import forms

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd] '
    'dark:[color-scheme:dark]'
)
_SELECT = _INPUT


class RegistroFrequenciaForm(forms.Form):
    turma          = forms.ModelChoiceField(
        label='Turma', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    materia        = forms.ModelChoiceField(
        label='Matéria', queryset=None, required=True,
        empty_label='— Selecione a matéria —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    professor      = forms.ModelChoiceField(
        label='Professor', queryset=None, required=False,
        empty_label='— Sem professor —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    ano_letivo     = forms.ModelChoiceField(
        label='Ano Letivo', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    periodo_letivo = forms.ModelChoiceField(
        label='Período Letivo', queryset=None, required=False,
        empty_label='— Selecione —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    data           = forms.DateField(
        label='Data da Aula',
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )

    def __init__(self, *args, escola=None, turma_ids=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.materia.models import Materia
        from apps.professor.models import PerfilProfessor
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo

        if escola:
            turma_qs = Turma.objects.filter(escola=escola, ativo=True).select_related('serie', 'ano_letivo').order_by('nome')
            if turma_ids is not None:
                turma_qs = turma_qs.filter(pk__in=turma_ids)
            series_ids = turma_qs.values_list('serie_id', flat=True)
            self.fields['turma'].queryset = turma_qs
            self.fields['materia'].queryset = (
                Materia.objects
                .filter(escola=escola, ativo=True,
                        series_config__serie_id__in=series_ids,
                        series_config__ativo=True)
                .distinct()
                .order_by('nome')
            )
            self.fields['professor'].queryset = (
                PerfilProfessor.objects
                .filter(papel__vinculo__escola=escola, papel__ativo=True)
                .select_related('papel__vinculo__usuario')
                .order_by('papel__vinculo__usuario__nome')
            )
            self.fields['ano_letivo'].queryset = (
                AnoLetivo.objects.filter(escola=escola).order_by('-ano')
            )
            self.fields['periodo_letivo'].queryset = (
                PeriodoLetivo.objects
                .filter(ano_letivo__escola=escola)
                .select_related('ano_letivo')
                .order_by('ano_letivo__ano', 'numero')
            )
        else:
            for f in ('turma', 'materia', 'professor', 'ano_letivo', 'periodo_letivo'):
                self.fields[f].queryset = self.fields[f].queryset.__class__.objects.none()
