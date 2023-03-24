from django import forms
from django.forms import CheckboxInput, TextInput

from .models import FrequenciaAluno


class FrequenciaAlunoForm(forms.ModelForm):

    class Meta:
        model = FrequenciaAluno
        fields = ('presente', 'observacao')
        widgets = {
            'observacao': TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(FrequenciaAlunoForm, self).__init__(*args, **kwargs)
        if instance:
            self.instance = instance
            self.fields['presente'].label = instance.aluno.nome
            self.fields['presente'].initial = instance.presente
            self.fields['observacao'].initial = instance.observacao



