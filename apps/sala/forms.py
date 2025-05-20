from django import forms

from ..sala.models import Sala


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ('descricao', 'turno', 'ano_letivo', 'ano')


class EditarSalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ('descricao', 'turno', 'ano')