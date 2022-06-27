import attrs as attrs
from django import forms
from django.forms import TextInput

from ..avaliacao.models import Resposta, Questao


class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ('resposta',)

        widgets = {
            'resposta': TextInput(
                attrs={
                    'size': '4px',
                    'style': 'margin-right: 6px; border: 1px solid #ccc; border-radius: 5px; padding: 4px 15px; margin: 4px; text-align: center;'
                }),
        }
