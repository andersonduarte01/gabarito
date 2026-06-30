from django import forms

from .models import Evento

_INPUT = 'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'


class EventoForm(forms.ModelForm):
    class Meta:
        model  = Evento
        fields = ['titulo', 'descricao', 'tipo', 'data_inicio', 'hora_inicio',
                  'data_fim', 'hora_fim', 'local', 'destinatarios', 'turmas']
        widgets = {
            'titulo':      forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Título do evento'}),
            'descricao':   forms.Textarea(attrs={'class': _INPUT, 'rows': 4, 'placeholder': 'Descrição (opcional)'}),
            'tipo':        forms.Select(attrs={'class': _INPUT}),
            'data_inicio': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
            'hora_inicio': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'data_fim':    forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}, format='%Y-%m-%d'),
            'hora_fim':    forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'local':       forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Local (opcional)'}),
            'destinatarios': forms.Select(attrs={'class': _INPUT, 'id': 'id_destinatarios'}),
            'turmas':      forms.CheckboxSelectMultiple(),
        }

    def __init__(self, escola=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if escola:
            from apps.turma.models import Turma
            from apps.ano_letivo.models import AnoLetivo, StatusAnoLetivo
            ano_ativo = AnoLetivo.objects.filter(
                escola=escola, status=StatusAnoLetivo.EM_ANDAMENTO
            ).first()
            qs = Turma.objects.filter(escola=escola, ativo=True)
            if ano_ativo:
                qs = qs.filter(ano_letivo=ano_ativo)
            self.fields['turmas'].queryset = qs

    def clean(self):
        cleaned = super().clean()
        data_inicio = cleaned.get('data_inicio')
        data_fim    = cleaned.get('data_fim')
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de término não pode ser anterior à data de início.')
        return cleaned
