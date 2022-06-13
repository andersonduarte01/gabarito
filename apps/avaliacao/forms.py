from django import forms
from django.forms import formset_factory
from django.forms.widgets import Input, TextInput

from ..avaliacao.models import Resposta


class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ('resposta',)
        widgets = {
            'resposta': TextInput(),
        }



