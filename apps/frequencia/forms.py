from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput, Textarea, DateInput, Select, IntegerField, HiddenInput, CharField, BooleanField
from django.forms import Form
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
            'pratica': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'campo': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data")
        data_fim = cleaned_data.get("data_fim")

        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValidationError("A data de início não pode ser maior que a data de fim.")


class RegistroUpdateForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ('data', 'data_fim', 'pratica', 'campo', 'objeto')
        widgets = {
            'data': TextInput(attrs={'class': 'form-control'}),
            'data_fim': TextInput(attrs={'class': 'form-control'}),
            'pratica': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'campo': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }



class RelatorioForm(forms.ModelForm):
    class Meta:
        model = Relatorio
        fields = ('relatorio', )
        widgets = {
            'relatorio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class FrequenciaForm(Form):
    aluno_id = IntegerField(widget=HiddenInput)
    nome = CharField(widget=HiddenInput())
    presente = BooleanField(required=False)
    observacao = CharField(
        required=False,
        max_length=255,
        widget=TextInput(attrs={'class': 'form-control'})
    )

