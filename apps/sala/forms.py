from django import forms

from apps.escola.forms import DaisyFormMixin
from apps.escola.models import AnoLetivo
from .models import Sala


class SalaForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Sala
        fields = ('descricao', 'turno', 'ano', 'ano_letivo')

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.filter(escola=escola)
        self.fields['ano'].required = False
        self.fields['ano_letivo'].empty_label = '— Selecione o ano letivo —'
