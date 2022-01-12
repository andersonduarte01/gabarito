from cProfile import label

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from apps import funcao
from apps.core.models import Usuario
from apps.direcao.models import DirecaoEscolar
from apps.escola.models import UnidadeEscolar
from apps.funcao.models import Funcao


class UserCreationDirecao(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)

    class Meta:
        model = DirecaoEscolar
        fields = ('email', 'nome', 'funcao')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Senhas não coincidem.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(UserCreationDirecao, self).__init__(*args, **kwargs)
        self.fields['funcao'].queryset = Funcao.objects.filter(escola=self.request.user)