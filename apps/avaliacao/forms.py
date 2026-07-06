from decimal import Decimal

from django import forms

from .models import ModalidadeAvaliacao, OpcaoResposta, Questao, TipoAvaliacao

_INPUT = (
    'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 '
    'border border-slate-200 dark:border-slate-700 rounded-lg '
    'text-slate-900 dark:text-slate-100 focus:outline-none '
    'focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'
)
_SELECT = _INPUT
_TEXTAREA = _INPUT + ' resize-none'


class AvaliacaoForm(forms.Form):
    titulo         = forms.CharField(
        label='Título', max_length=200,
        widget=forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Prova Bimestral de Matemática'}),
    )
    tipo           = forms.ChoiceField(
        label='Tipo', choices=TipoAvaliacao.choices,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    modalidade     = forms.ChoiceField(
        label='Modalidade', choices=ModalidadeAvaliacao.choices,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    turma          = forms.ModelChoiceField(
        label='Turma', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    materia        = forms.ModelChoiceField(
        label='Matéria', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    professor      = forms.ModelChoiceField(
        label='Professor', queryset=None, required=False, empty_label='— Sem professor —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    ano_letivo     = forms.ModelChoiceField(
        label='Ano Letivo', queryset=None,
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    periodo_letivo = forms.ModelChoiceField(
        label='Período Letivo', queryset=None, required=False, empty_label='— Selecione —',
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    data_aplicacao = forms.DateField(
        label='Data de Aplicação', required=False,
        widget=forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
    )
    nota_maxima    = forms.DecimalField(
        label='Nota Máxima', max_digits=5, decimal_places=2, initial=Decimal('10.00'),
        widget=forms.NumberInput(attrs={'class': _INPUT, 'step': '0.5'}),
    )
    peso           = forms.DecimalField(
        label='Peso', max_digits=5, decimal_places=2, initial=Decimal('1.00'),
        widget=forms.NumberInput(attrs={'class': _INPUT, 'step': '0.5'}),
    )

    def __init__(self, *args, escola=None, instance=None, turma_ids=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.turma.models import Turma
        from apps.materia.models import Materia
        from apps.professor.models import PerfilProfessor
        from apps.ano_letivo.models import AnoLetivo, PeriodoLetivo

        if escola:
            turma_qs = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
            if turma_ids is not None:
                turma_qs = turma_qs.filter(pk__in=turma_ids)
            self.fields['turma'].queryset          = turma_qs
            self.fields['materia'].queryset        = Materia.objects.filter(escola=escola, ativo=True).order_by('nome')
            self.fields['professor'].queryset      = (
                PerfilProfessor.objects
                .filter(papel__vinculo__escola=escola, papel__ativo=True)
                .select_related('papel__vinculo__usuario')
                .order_by('papel__vinculo__usuario__nome')
            )
            self.fields['ano_letivo'].queryset     = AnoLetivo.objects.filter(escola=escola).order_by('-ano')
            self.fields['periodo_letivo'].queryset = (
                PeriodoLetivo.objects
                .filter(ano_letivo__escola=escola)
                .select_related('ano_letivo')
                .order_by('ano_letivo__ano', 'numero')
            )
        else:
            for f in ('turma', 'materia', 'professor', 'ano_letivo', 'periodo_letivo'):
                self.fields[f].queryset = self.fields[f].queryset.none()

        if instance:
            self.initial.update({
                'titulo':         instance.titulo,
                'tipo':           instance.tipo,
                'modalidade':     instance.modalidade,
                'turma':          instance.turma_id,
                'materia':        instance.materia_id,
                'professor':      instance.professor_id,
                'ano_letivo':     instance.ano_letivo_id,
                'periodo_letivo': instance.periodo_letivo_id,
                'data_aplicacao': instance.data_aplicacao,
                'nota_maxima':    instance.nota_maxima,
                'peso':           instance.peso,
            })


class QuestaoForm(forms.ModelForm):
    class Meta:
        model   = Questao
        fields  = ('numero', 'enunciado', 'tipo', 'pontuacao')
        widgets = {
            'numero':    forms.NumberInput(attrs={'class': _INPUT, 'min': 1}),
            'enunciado': forms.Textarea(attrs={'class': _TEXTAREA, 'rows': 3}),
            'tipo':      forms.Select(attrs={'class': _SELECT}),
            'pontuacao': forms.NumberInput(attrs={'class': _INPUT, 'step': '0.5'}),
        }


class OpcaoRespostaForm(forms.ModelForm):
    class Meta:
        model   = OpcaoResposta
        fields  = ('letra', 'texto', 'correta')
        widgets = {
            'letra':   forms.TextInput(attrs={'class': _INPUT, 'maxlength': 1, 'placeholder': 'A'}),
            'texto':   forms.TextInput(attrs={'class': _INPUT}),
            'correta': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-[#0d6efd]'}),
        }
