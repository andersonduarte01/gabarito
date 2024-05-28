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


class DateInput(forms.DateInput):
    input_type = 'date'

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'data_fim', 'pratica', 'campo', 'objeto')
        widgets = {
            'data': DateInput(attrs={'class': 'form-control'}),
            'data_fim': DateInput(attrs={'class': 'form-control'}),
            'pratica': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'campo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'data_fim', 'pratica', 'campo', 'objeto')
        widgets = {
            'data': DateInput(attrs={'class': 'form-control'}),
            'data_fim': DateInput(attrs={'class': 'form-control'}),
            'pratica': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'campo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class RegistroUpdateForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'data_fim', 'pratica', 'campo', 'objeto')



class RelatorioForm(forms.ModelForm):
    class Meta:
        model = Relatorio
        fields = ('relatorio', )
