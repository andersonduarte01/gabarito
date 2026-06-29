from django import forms

from apps.materia.models import Materia
from apps.serie.models import Serie

_INPUT = (
    'w-full rounded-xl border border-slate-200 dark:border-slate-700 '
    'bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 '
    'placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6efd]/30 '
    'focus:border-[#0d6efd] transition'
)


class MateriaForm(forms.ModelForm):
    class Meta:
        model   = Materia
        fields  = ['nome', 'codigo']
        widgets = {
            'nome':   forms.TextInput(attrs={
                'class': _INPUT,
                'placeholder': 'Ex: Matematica',
            }),
            'codigo': forms.TextInput(attrs={
                'class': _INPUT,
                'placeholder': 'Ex: MAT (opcional)',
            }),
        }


class VincularSerieForm(forms.Form):
    serie = forms.ModelChoiceField(
        queryset=Serie.objects.none(),
        label='Serie',
        empty_label='Selecione a serie...',
        widget=forms.Select(attrs={'class': _INPUT}),
    )

    def __init__(self, *args, materia=None, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materia and escola:
            ja_vinculadas = materia.series_config.filter(ativo=True).values_list('serie_id', flat=True)
            self.fields['serie'].queryset = (
                Serie.objects
                .filter(escola=escola, ativo=True)
                .exclude(pk__in=ja_vinculadas)
                .select_related('segmento')
                .order_by('segmento__tipo', 'ordem')
            )
