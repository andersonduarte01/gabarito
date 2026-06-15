from django import forms
from .models import Noticia


class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'resumo', 'categoria', 'imagem', 'destaque', 'status', 'visibilidade', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Título da notícia',
                'autofocus': True,
            }),
            'resumo': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Breve descrição exibida nos cards (opcional)...',
            }),
            'categoria': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'visibilidade': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'imagem': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'toggle toggle-primary',
            }),
        }
