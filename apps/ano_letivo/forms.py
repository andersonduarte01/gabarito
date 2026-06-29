from django import forms

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)

_DATE_FORMATS = ['%Y-%m-%d', '%d/%m/%Y']


class AnoLetivoForm(forms.Form):
    ano = forms.IntegerField(
        label='Ano',
        min_value=2000,
        max_value=2050,
        widget=forms.NumberInput(attrs={'class': _INPUT, 'placeholder': '2025'}),
    )
    data_inicio = forms.DateField(
        label='Data de Início',
        input_formats=_DATE_FORMATS,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    data_fim = forms.DateField(
        label='Data de Fim',
        input_formats=_DATE_FORMATS,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim    = cleaned_data.get('data_fim')
        if data_inicio and data_fim and data_inicio >= data_fim:
            raise forms.ValidationError('A data de início deve ser anterior à data de fim.')
        return cleaned_data


class PeriodoLetivoForm(forms.Form):
    numero = forms.IntegerField(
        label='Número do Período',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': _INPUT, 'placeholder': '1'}),
    )
    nome = forms.CharField(
        label='Nome',
        max_length=50,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: 1º Bimestre'}),
    )
    data_inicio = forms.DateField(
        label='Data de Início',
        input_formats=_DATE_FORMATS,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    data_fim = forms.DateField(
        label='Data de Fim',
        input_formats=_DATE_FORMATS,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim    = cleaned_data.get('data_fim')
        if data_inicio and data_fim and data_inicio >= data_fim:
            raise forms.ValidationError('A data de início deve ser anterior à data de fim.')
        return cleaned_data
