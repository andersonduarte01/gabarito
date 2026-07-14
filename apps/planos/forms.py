from datetime import date

from django import forms

from .models import AssinaturaEscola, Modulo, Plano

INPUT    = 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors dark:[color-scheme:dark]'
TEXTAREA = INPUT + ' resize-none'
SELECT   = INPUT


class PlanoForm(forms.ModelForm):
    class Meta:
        model   = Plano
        fields  = ['nome', 'descricao', 'preco_mensal', 'modulos', 'ativo']
        widgets = {
            'nome':         forms.TextInput(attrs={'class': INPUT}),
            'descricao':    forms.Textarea(attrs={'class': TEXTAREA, 'rows': 3}),
            'preco_mensal': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'modulos':      forms.CheckboxSelectMultiple(),
            'ativo':        forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded text-[#0d6efd]'}),
        }


class AssinaturaAtivarForm(forms.Form):
    plano           = forms.ModelChoiceField(
        queryset=Plano.objects.filter(ativo=True),
        label='Plano',
        widget=forms.Select(attrs={'class': SELECT}),
    )
    data_vencimento = forms.DateField(
        label='Data de vencimento',
        widget=forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
    )
    observacao      = forms.CharField(
        label='Observação (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA, 'rows': 2}),
    )

    def clean_data_vencimento(self):
        valor = self.cleaned_data['data_vencimento']
        if valor <= date.today():
            raise forms.ValidationError('A data de vencimento deve ser futura.')
        return valor


class AssinaturaGraceForm(forms.Form):
    observacao = forms.CharField(
        label='Observação (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA, 'rows': 2}),
    )


class AssinaturaSuspenderForm(forms.Form):
    observacao = forms.CharField(
        label='Motivo da suspensão',
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA, 'rows': 2}),
    )


class AssinaturaCancelarForm(forms.Form):
    observacao = forms.CharField(
        label='Motivo do cancelamento',
        required=False,
        widget=forms.Textarea(attrs={'class': TEXTAREA, 'rows': 2}),
    )
