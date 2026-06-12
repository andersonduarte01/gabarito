# forms.py
from django import forms
from django.utils.timezone import now

from ..core.models import Usuario
from ..escola.models import UnidadeEscolar, EnderecoEscolar, UsuarioEscola


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


class CriarEscolaForm(forms.ModelForm):
    class Meta:
        model = UnidadeEscolar
        fields = ('nome_escola', 'inep', 'cnpj', 'telefone')
        widgets = {
            'nome_escola': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da escola'}),
            'inep':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código INEP'}),
            'cnpj':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'telefone':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(88) 9 8888-8888'}),
        }


class CriarAdminEscolaForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do administrador'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@escola.com'}),
    )
    escola = forms.ModelChoiceField(
        label='Escola',
        queryset=UnidadeEscolar.objects.filter(ativa=True).order_by('nome_escola'),
        empty_label='Selecione a escola…',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    senha = forms.CharField(
        label='Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 8 caracteres'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado no sistema.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('senha') != cleaned.get('confirmar_senha'):
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned


class CadastrarUsuarioForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do usuário'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@email.com'}),
    )
    senha = forms.CharField(
        label='Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 8 caracteres'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    tipo = forms.ChoiceField(
        label='Perfil de acesso',
        choices=UsuarioEscola.TIPOS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado no sistema.')
        return email

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return cleaned
