from django import forms

from apps.escola.models import SegmentoEscolar
from apps.serie.models import Serie

_INPUT = (
    'w-full rounded-xl border border-slate-200 dark:border-slate-700 '
    'bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 '
    'placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0d6efd]/30 '
    'focus:border-[#0d6efd] transition'
)


class CriarSerieForm(forms.Form):
    segmento = forms.ModelChoiceField(
        queryset=SegmentoEscolar.objects.none(),
        label='Segmento',
        empty_label='Selecione o segmento',
        widget=forms.Select(attrs={'class': _INPUT}),
    )
    nome = forms.CharField(
        max_length=100,
        label='Nome',
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: 1º Ano'}),
    )
    ordem = forms.IntegerField(
        min_value=1,
        label='Ordem',
        widget=forms.NumberInput(attrs={'class': _INPUT, 'min': 1}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['segmento'].queryset = (
                SegmentoEscolar.objects.filter(escola=escola).order_by('tipo')
            )


class EditarSerieForm(forms.ModelForm):
    class Meta:
        model  = Serie
        fields = ['nome', 'ordem']
        widgets = {
            'nome':  forms.TextInput(attrs={
                'class': _INPUT,
                'placeholder': 'Ex: 1º Ano',
            }),
            'ordem': forms.NumberInput(attrs={
                'class': _INPUT,
                'min': 1,
            }),
        }
