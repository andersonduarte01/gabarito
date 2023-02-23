from django import forms
from django.forms import CheckboxInput, TextInput, HiddenInput

from .models import FrequenciaAluno


class AlunoForm(forms.ModelForm):

    class Meta:
        model = FrequenciaAluno
        fields = ('presente', 'falta_justificada', 'observacao')

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(AlunoForm, self).__init__(*args, **kwargs)
        if instance:
            self.instance = instance
            self.fields['presente'].label = instance.aluno.nome
            self.fields['presente'].initial = instance.presente
            self.fields['falta_justificada'].initial = instance.falta_justificada
            self.fields['observacao'].initial = instance.observacao



