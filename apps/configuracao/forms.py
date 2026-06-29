from django import forms

from .models import (
    ConfiguracaoAcademica,
    ConfiguracaoFrequencia,
    ConfiguracaoProfessor,
)

INPUT  = 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors'
SELECT = INPUT
CHECK  = 'w-4 h-4 rounded text-[#0d6efd]'


class AcademicaForm(forms.ModelForm):
    class Meta:
        model  = ConfiguracaoAcademica
        fields = [
            'nota_maxima', 'nota_minima_aprovacao',
            'tipo_periodo_letivo', 'casas_decimais_nota',
            'tipo_calculo_media',
            'exige_recuperacao', 'nota_minima_recuperacao',
        ]
        widgets = {
            'nota_maxima':             forms.NumberInput(attrs={'class': INPUT, 'step': '0.1'}),
            'nota_minima_aprovacao':   forms.NumberInput(attrs={'class': INPUT, 'step': '0.1'}),
            'tipo_periodo_letivo':     forms.Select(attrs={'class': SELECT}),
            'casas_decimais_nota':     forms.Select(
                attrs={'class': SELECT},
                choices=[(0, '0 casas (ex: 7)'), (1, '1 casa (ex: 7,5)'), (2, '2 casas (ex: 7,50)')],
            ),
            'tipo_calculo_media':      forms.Select(attrs={'class': SELECT}),
            'exige_recuperacao':       forms.CheckboxInput(attrs={'class': CHECK}),
            'nota_minima_recuperacao': forms.NumberInput(attrs={'class': INPUT, 'step': '0.1'}),
        }


class FrequenciaForm(forms.ModelForm):
    class Meta:
        model  = ConfiguracaoFrequencia
        fields = [
            'percentual_minimo_frequencia',
            'percentual_alerta_prevencao',
            'modo_lancamento',
        ]
        widgets = {
            'percentual_minimo_frequencia': forms.NumberInput(attrs={'class': INPUT, 'step': '0.1', 'min': '0', 'max': '100'}),
            'percentual_alerta_prevencao':  forms.NumberInput(attrs={'class': INPUT, 'step': '0.1', 'min': '0', 'max': '100'}),
            'modo_lancamento':              forms.Select(attrs={'class': SELECT}),
        }

    def clean(self):
        cleaned = super().clean()
        minimo  = cleaned.get('percentual_minimo_frequencia')
        alerta  = cleaned.get('percentual_alerta_prevencao')
        if minimo is not None and alerta is not None and alerta <= minimo:
            self.add_error(
                'percentual_alerta_prevencao',
                'O percentual de alerta deve ser maior que o mínimo legal.',
            )
        return cleaned


class ProfessorForm(forms.ModelForm):
    class Meta:
        model  = ConfiguracaoProfessor
        fields = ['carga_horaria_maxima_semanal']
        widgets = {
            'carga_horaria_maxima_semanal': forms.NumberInput(
                attrs={'class': INPUT, 'min': '1', 'max': '80'}
            ),
        }
