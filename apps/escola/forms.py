from django import forms

from .models import EnderecoEscolar, TipoSegmento, UnidadeEscolar

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT = _INPUT
_COLOR = (
    'h-9 w-16 p-0.5 rounded-lg cursor-pointer '
    'border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800'
)

ESTADOS_BR = [
    ('', 'Selecione'),
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
    ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
    ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'),
    ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]


class EscolaForm(forms.ModelForm):
    class Meta:
        model  = UnidadeEscolar
        fields = [
            'nome', 'nome_curto', 'cnpj', 'tipo',
            'telefone', 'email', 'site', 'logo',
            'cor_primaria', 'cor_secundaria', 'cor_acento',
        ]
        widgets = {
            'nome':           forms.TextInput(attrs={'class': _INPUT}),
            'nome_curto':     forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Sigla ou nome abreviado'}),
            'cnpj':           forms.TextInput(attrs={'class': _INPUT, 'placeholder': '00.000.000/0000-00'}),
            'tipo':           forms.Select(attrs={'class': _SELECT}),
            'telefone':       forms.TextInput(attrs={'class': _INPUT, 'placeholder': '(00) 0000-0000'}),
            'email':          forms.EmailInput(attrs={'class': _INPUT}),
            'site':           forms.URLInput(attrs={'class': _INPUT, 'placeholder': 'https://'}),
            'cor_primaria':   forms.TextInput(attrs={'type': 'color', 'class': _COLOR}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color', 'class': _COLOR}),
            'cor_acento':     forms.TextInput(attrs={'type': 'color', 'class': _COLOR}),
        }


class EnderecoEscolarForm(forms.ModelForm):
    uf = forms.ChoiceField(
        choices=ESTADOS_BR,
        widget=forms.Select(attrs={'class': _SELECT}),
        label='UF',
    )

    class Meta:
        model  = EnderecoEscolar
        fields = ['nome', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'municipio', 'uf']
        widgets = {
            'nome':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Sede, Anexo, Quadra'}),
            'cep':         forms.TextInput(attrs={'class': _INPUT, 'placeholder': '00000-000'}),
            'logradouro':  forms.TextInput(attrs={'class': _INPUT}),
            'numero':      forms.TextInput(attrs={'class': _INPUT}),
            'complemento': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Opcional'}),
            'bairro':      forms.TextInput(attrs={'class': _INPUT}),
            'municipio':   forms.TextInput(attrs={'class': _INPUT}),
        }


class AdicionarSegmentoForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': _SELECT}),
        label='Segmento',
    )

    def __init__(self, *args, existentes=None, **kwargs):
        super().__init__(*args, **kwargs)
        usados = set(existentes or [])
        disponiveis = [
            (v, l) for v, l in TipoSegmento.choices if v not in usados
        ]
        self.fields['tipo'].choices = [('', 'Selecione')] + disponiveis
