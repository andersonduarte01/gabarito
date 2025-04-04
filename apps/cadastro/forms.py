from django import forms
from ..cadastro.models import CadastroInicio, CadUnificado, RG, Endereco, Profissional
from django.core.exceptions import ValidationError

from ..escola.models import UnidadeEscolar


class CadastramentoForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)
    nome = forms.CharField(
        label='Nome Completo',  # Alterando a label
        widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome completo'})  # Alterando o placeholder
    )

    class Meta:
        model = CadastroInicio
        fields = ('nome', 'cpf', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Senhas não coincidem.")
        return password2


class UnicoForm(forms.ModelForm):
    class Meta:
        model = CadUnificado
        fields = ('foto', 'data_nascimento', 'sexo', 'telefone')


class RGForm(forms.ModelForm):
    class Meta:
        model = RG
        fields = ('rg_cnh', 'numero', 'emissao', 'cpf')


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ('comprovate', 'area', 'rua', 'numero', 'bairro', 'complemento', 'localidade_sitio')

    # Aplicando a classe bootstrap manualmente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ('vinculo', 'nomeacao',  'funcao', 'lotado', 'data_admissao', 'experiencia')

    # Aplicando a classe bootstrap manualmente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
