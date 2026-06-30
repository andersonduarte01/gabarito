from django import forms

from .models import Comunicado, DestinatarioComunicado

_INPUT = 'w-full px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#0d6efd]/30 focus:border-[#0d6efd]'


class ComunicadoForm(forms.ModelForm):
    class Meta:
        model  = Comunicado
        fields = ['titulo', 'corpo', 'tipo', 'destinatarios', 'turmas']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Título do comunicado'}),
            'corpo':  forms.Textarea(attrs={'class': _INPUT, 'rows': 6, 'placeholder': 'Conteúdo do comunicado...'}),
            'tipo':   forms.Select(attrs={'class': _INPUT}),
            'destinatarios': forms.Select(attrs={'class': _INPUT, 'id': 'id_destinatarios'}),
            'turmas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, escola=None, papel=None, *args, **kwargs):
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
            if papel and papel.tipo == 'PROFESSOR':
                from apps.turma.models import ProfessorTurma, ProfessorMateriaTurma
                from apps.professor.models import PerfilProfessor
                try:
                    perfil = PerfilProfessor.objects.get(papel=papel)
                    turmas_ids = set(
                        ProfessorTurma.objects.filter(professor=perfil, ativo=True).values_list('turma_id', flat=True)
                    ) | set(
                        ProfessorMateriaTurma.objects.filter(professor=perfil, ativo=True).values_list('turma_id', flat=True)
                    )
                    qs = qs.filter(id__in=turmas_ids)
                    self.fields['destinatarios'].choices = [
                        c for c in DestinatarioComunicado.choices
                        if c[0] != DestinatarioComunicado.TODOS
                    ]
                except PerfilProfessor.DoesNotExist:
                    pass
            self.fields['turmas'].queryset = qs
