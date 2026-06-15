from django import forms

from apps.escola.forms import DaisyFormMixin
from .models import Diretor


class DiretorForm(DaisyFormMixin, forms.ModelForm):

    class Meta:
        model = Diretor
        fields = ['foto', 'cpf', 'telefone']
        labels = {
            'foto':     'Foto de perfil',
            'cpf':      'CPF',
            'telefone': 'Telefone',
        }
        help_texts = {
            'cpf':      'Somente números. Ex: 12345678901',
            'telefone': 'DDD + número. Ex: 88999999999',
        }
