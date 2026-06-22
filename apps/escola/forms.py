from django import forms
from django.utils.timezone import now

from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ESTADOS_BR = [
    ('', 'Selecione o estado'),
    ('AC', 'Acre'),          ('AL', 'Alagoas'),       ('AP', 'Amapá'),
    ('AM', 'Amazonas'),      ('BA', 'Bahia'),          ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
    ('MA', 'Maranhão'),      ('MT', 'Mato Grosso'),   ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),  ('PA', 'Pará'),           ('PB', 'Paraíba'),
    ('PR', 'Paraná'),        ('PE', 'Pernambuco'),     ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),      ('RR', 'Roraima'),        ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),     ('SE', 'Sergipe'),        ('TO', 'Tocantins'),
]

MESES = [
    (1, 'Janeiro'),  (2, 'Fevereiro'), (3, 'Março'),     (4, 'Abril'),
    (5, 'Maio'),     (6, 'Junho'),     (7, 'Julho'),      (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'),  (12, 'Dezembro'),
]


# ---------------------------------------------------------------------------
# Mixin de widgets DaisyUI — reutilizável em qualquer form do projeto
# ---------------------------------------------------------------------------

class DaisyFormMixin:
    """
    Aplica automaticamente as classes DaisyUI nos widgets de todos os campos.
    Basta herdar junto com forms.ModelForm ou forms.Form.
    """

    WIDGET_CLASSES = {
        forms.TextInput:     'input input-bordered w-full',
        forms.EmailInput:    'input input-bordered w-full',
        forms.URLInput:      'input input-bordered w-full',
        forms.NumberInput:   'input input-bordered w-full',
        forms.DateInput:     'input input-bordered w-full',
        forms.PasswordInput: 'input input-bordered w-full',
        forms.Select:        'select select-bordered w-full',
        forms.Textarea:      'textarea textarea-bordered w-full',
        forms.FileInput:     'file-input file-input-bordered w-full',
        forms.CheckboxInput: 'checkbox checkbox-primary',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget_type = type(field.widget)
            css = self.WIDGET_CLASSES.get(widget_type)
            if css:
                field.widget.attrs.setdefault('class', css)


# ---------------------------------------------------------------------------
# Formulários da escola
# ---------------------------------------------------------------------------

class EscolaForm(DaisyFormMixin, forms.ModelForm):

    class Meta:
        model  = UnidadeEscolar
        fields = (
            'nome_escola', 'tipo', 'inep', 'cnpj',
            'telefone', 'email', 'site', 'logo_escola',
        )
        labels = {
            'nome_escola': 'Nome da escola',
            'tipo':        'Tipo de escola',
            'inep':        'Código INEP',
            'cnpj':        'CNPJ',
            'telefone':    'Telefone',
            'email':       'E-mail institucional',
            'site':        'Site',
            'logo_escola': 'Logo',
        }
        help_texts = {
            'cnpj':     'Somente números. Ex: 12345678000195',
            'telefone': 'DDD + número. Ex: 88999999999',
            'inep':     'Código INEP de 8 dígitos da escola.',
        }

    def clean_cnpj(self):
        from apps.core.validators import normalizar_cnpj, validate_cnpj
        cnpj = normalizar_cnpj(self.cleaned_data.get('cnpj'))
        if cnpj:
            validate_cnpj(cnpj)
        return cnpj

    def clean_telefone(self):
        from apps.core.validators import normalizar_telefone, validate_telefone
        telefone = normalizar_telefone(self.cleaned_data.get('telefone'))
        if telefone:
            validate_telefone(telefone)
        return telefone


class EnderecoEscolarForm(DaisyFormMixin, forms.ModelForm):

    estado = forms.ChoiceField(
        choices=ESTADOS_BR,
        label='Estado',
    )

    class Meta:
        model  = EnderecoEscolar
        fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')
        labels = {
            'rua':         'Rua / Avenida',
            'numero':      'Número',
            'complemento': 'Complemento',
            'bairro':      'Bairro',
            'cep':         'CEP',
            'cidade':      'Cidade',
        }
        help_texts = {
            'cep':         'Somente números. Ex: 63100000',
            'complemento': 'Opcional. Ex: Bloco A, Sala 2.',
        }

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '').replace('-', '').strip()
        if cep and len(cep) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        return cep


class AnoLetivoForm(DaisyFormMixin, forms.ModelForm):

    class Meta:
        model  = AnoLetivo
        fields = ('ano', 'inicio', 'fim', 'corrente', 'descricao')
        labels = {
            'ano':       'Ano letivo',
            'inicio':    'Data de início',
            'fim':       'Data de término',
            'corrente':  'Definir como ano letivo corrente',
            'descricao': 'Observações',
        }
        widgets = {
            'ano':      forms.NumberInput(attrs={
                'placeholder': 'Ex: 2026',
                'min': '2000',
                'max': '2099',
            }),
            'inicio':    forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fim':       forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'corrente':  forms.CheckboxInput(attrs={
                'class': 'toggle toggle-primary',
                'role':  'switch',
            }),
            'descricao': forms.Textarea(attrs={
                'rows':        3,
                'placeholder': 'Informações adicionais sobre o ano letivo (opcional).',
            }),
        }

    def clean_ano(self):
        ano = self.cleaned_data.get('ano')
        if ano is not None and not (2000 <= ano <= 2099):
            raise forms.ValidationError('Informe um ano válido entre 2000 e 2099.')
        return ano

    def clean(self):
        cleaned = super().clean()
        inicio  = cleaned.get('inicio')
        fim     = cleaned.get('fim')
        if inicio and fim and fim <= inicio:
            raise forms.ValidationError(
                {'fim': 'A data de término deve ser posterior à data de início.'}
            )
        return cleaned


class FiltroMesForm(DaisyFormMixin, forms.Form):

    mes = forms.ChoiceField(
        choices=MESES,
        initial=now().month,
        label='Mês',
    )
