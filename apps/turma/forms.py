from django import forms

from apps.ano_letivo.models import AnoLetivo
from apps.serie.models import Serie
from apps.turma.models import Turma, Turno

INPUT  = 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors'
SELECT = INPUT


class PeriodoAulaForm(forms.Form):
    numero = forms.IntegerField(
        label='Nº',
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': INPUT, 'placeholder': '1'}),
    )
    nome = forms.CharField(
        label='Nome',
        max_length=50,
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': '1° Período'}),
    )
    hora_inicio = forms.TimeField(
        label='Início',
        widget=forms.TimeInput(attrs={'class': INPUT, 'type': 'time'}),
    )
    hora_fim = forms.TimeField(
        label='Fim',
        widget=forms.TimeInput(attrs={'class': INPUT, 'type': 'time'}),
    )


class TurmaForm(forms.Form):
    ano_letivo = forms.ModelChoiceField(
        queryset=AnoLetivo.objects.none(),
        label='Ano Letivo',
        widget=forms.Select(attrs={'class': SELECT}),
    )
    serie = forms.ModelChoiceField(
        queryset=Serie.objects.none(),
        label='Série',
        widget=forms.Select(attrs={'class': SELECT}),
    )
    nome = forms.CharField(
        label='Nome / Identificador',
        max_length=50,
        help_text='Ex: A, B, 01, Manhã',
        widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ex: A'}),
    )
    turno = forms.ChoiceField(
        label='Turno',
        choices=Turno.choices,
        widget=forms.Select(attrs={'class': SELECT}),
    )
    capacidade = forms.IntegerField(
        label='Capacidade (opcional)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': INPUT, 'placeholder': 'Sem limite'}),
    )

    def __init__(self, *args, escola=None, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            self.fields['ano_letivo'].queryset = (
                AnoLetivo.objects
                .filter(escola=escola)
                .exclude(status='ENCERRADO')
                .order_by('-ano')
            )
            self.fields['serie'].queryset = (
                Serie.objects
                .filter(escola=escola, ativo=True)
                .select_related('segmento')
                .order_by('segmento__tipo', 'ordem')
            )

    def clean(self):
        cleaned = super().clean()
        ano     = cleaned.get('ano_letivo')
        serie   = cleaned.get('serie')
        nome    = cleaned.get('nome')
        turno   = cleaned.get('turno')
        instance = self.instance if hasattr(self, 'instance') else None

        if ano and serie and nome and turno:
            qs = Turma.objects.filter(
                ano_letivo=ano, serie=serie, nome=nome, turno=turno,
            )
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'Já existe uma turma com essa combinação de série, nome e turno neste ano letivo.'
                )
        return cleaned
