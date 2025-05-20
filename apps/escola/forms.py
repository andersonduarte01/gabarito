# forms.py
from django import forms
from django.utils.timezone import now

from ..core.models import Usuario
from ..escola.models import UnidadeEscolar, EnderecoEscolar


class FiltroMesForm(forms.Form):
    MESES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]

    mes = forms.ChoiceField(
        choices=MESES,
        initial=now().month,
        label='Selecione o mês',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control w-100'})
    )


class EscolaForm(forms.ModelForm):
    class Meta:
        model = UnidadeEscolar
        fields = ('nome_escola', 'inep', 'cnpj', 'telefone', 'logo_escola')


class EnderecoForm1(forms.ModelForm):
    class Meta:
        model = EnderecoEscolar
        fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nome')
