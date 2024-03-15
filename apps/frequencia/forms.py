from django import forms
from django.forms import TextInput, Textarea, DateInput, Select

from .models import FrequenciaAluno, Registro, Relatorio


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


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'pratica', 'campo', 'objeto')
        widgets = {
            'pratica': Textarea(attrs={'rows': 4}),
            'campo': Textarea(attrs={'rows': 4}),
            'objeto': Textarea(attrs={'rows': 4}),
        }


class RegistroUpdateForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'pratica', 'campo', 'objeto')
        widgets = {
            'pratica': Textarea(attrs={'rows': 4}),
            'campo': Textarea(attrs={'rows': 4}),
            'objeto': Textarea(attrs={'rows': 4}),
        }


class RelatorioForm(forms.ModelForm):
    class Meta:
        model = Relatorio
        fields = ('relatorio', )
