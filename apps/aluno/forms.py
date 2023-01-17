from django import forms

from ..aluno.models import Aluno
from ..sala.models import Sala


class DesignarSalaForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ('nome', 'sala')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(DesignarSalaForm, self).__init__(*args, **kwargs)
        self.fields['sala'].queryset = Sala.objects.filter(escola=self.request.user)


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ('nome', 'sala')

    def __init__(self, *args, **kwargs):
        escola = kwargs.pop('escola')
        super(AlunoForm, self).__init__(*args, **kwargs)
        self.fields['sala'].queryset = Sala.objects.filter(escola=escola)
