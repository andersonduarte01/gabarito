from django import forms

from .models import Arquivo, CategoriaArquivo, Livro, Video


class ArquivoForm(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = ['titulo', 'descricao', 'pdf', 'publico', 'visibilidade']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Título do arquivo',
                'autofocus': True,
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Descrição opcional...',
            }),
            'pdf': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'application/pdf',
            }),
            'publico': forms.CheckboxInput(attrs={
                'class': 'toggle toggle-primary',
            }),
            'visibilidade': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
        }


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'descricao', 'categoria', 'autor', 'editora', 'ano_referencia', 'pdf', 'visibilidade']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Título do livro',
                'autofocus': True,
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Sinopse ou observações...',
            }),
            'categoria': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'autor': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nome do autor',
            }),
            'editora': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Editora (opcional)',
            }),
            'ano_referencia': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'pdf': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'application/pdf',
            }),
            'visibilidade': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['numero', 'titulo', 'url_video', 'ano', 'materia', 'sigla', 'professor', 'duracao']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ex: 01',
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Título do vídeo',
                'autofocus': True,
            }),
            'url_video': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://youtube.com/...',
            }),
            'ano': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'materia': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ex: Matemática',
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ex: MAT',
            }),
            'professor': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nome do professor(a)',
            }),
            'duracao': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ex: 15:30',
            }),
        }


class CategoriaArquivoForm(forms.ModelForm):
    class Meta:
        model = CategoriaArquivo
        fields = ['titulo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nome da categoria',
                'autofocus': True,
            }),
        }
