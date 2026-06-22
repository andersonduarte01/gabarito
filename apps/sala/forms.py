from django import forms

from apps.escola.forms import DaisyFormMixin
from apps.escola.models import AnoLetivo
from .models import Turma, SERIE_CHOICES


class TurmaForm(DaisyFormMixin, forms.ModelForm):

    class Meta:
        model = Turma
        fields = ('nome', 'serie', 'turno', 'ano_letivo', 'capacidade', 'ativo')
        labels = {
            'nome':       'Nome da turma',
            'serie':      'Série',
            'turno':      'Turno',
            'ano_letivo': 'Ano letivo',
            'capacidade': 'Capacidade máxima',
            'ativo':      'Turma ativa',
        }
        widgets = {
            'ativo': forms.CheckboxInput(attrs={
                'class': 'toggle toggle-primary',
                'role':  'switch',
            }),
        }

    def __init__(self, *args, escola=None, modo='criar', **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            qs = AnoLetivo.objects.filter(escola=escola)
            if modo == 'criar':
                qs = qs.filter(corrente=True)
            self.fields['ano_letivo'].queryset = qs.order_by('-ano')
        else:
            self.fields['ano_letivo'].queryset = AnoLetivo.objects.none()
        self.fields['serie'].required = False
        self.fields['serie'].choices = [('', '— Selecione a série —')] + SERIE_CHOICES
        self.fields['ano_letivo'].empty_label = '— Selecione o ano letivo —'
        self.fields['capacidade'].required = False
