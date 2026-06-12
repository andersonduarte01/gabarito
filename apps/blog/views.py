from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from unidecode import unidecode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView

from ..arquivos.models import Arquivo, Livro
from ..arquivos.models import Categoria as CategoriaArquivo
from ..blog.models import Video
from ..sala.models import Ano

from .models import Blog, Categoria


# ── Público ────────────────────────────────────────────────────────────────

class Index(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['noticias_recentes'] = Blog.objects.select_related('autor', 'categoria').order_by('-data')[:4]
        return context


class Sobre(TemplateView):
    template_name = 'blog/sobre.html'


class Contato(TemplateView):
    template_name = 'blog/contate_nos.html'


# ── Notícias ───────────────────────────────────────────────────────────────

class Noticias(ListView):
    model = Blog
    template_name = 'blog/blog.html'
    context_object_name = 'noticias'
    paginate_by = 8

    def get_queryset(self):
        qs = Blog.objects.select_related('autor', 'categoria').order_by('-data')
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(Q(titulo__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class ResultadoNoticias(Noticias):
    pass


class Noticia(DetailView):
    model = Blog
    template_name = 'blog/noticia.html'
    context_object_name = 'noticia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temas'] = Categoria.objects.all()
        context['recentes'] = Blog.objects.exclude(pk=self.object.pk).order_by('-data')[:3]
        return context


class AddNoticia(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = reverse_lazy('blog:noticias')

    def form_valid(self, form):
        noticia = form.save(commit=False)
        slug_base = unidecode(noticia.titulo).lower()
        for ch in [':', ';', ',']:
            slug_base = slug_base.replace(ch, '')
        noticia.slug = slug_base.replace(' ', '-')
        noticia.autor = self.request.user
        noticia.save()
        return super().form_valid(form)


class EditNoticia(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = reverse_lazy('blog:noticias')


# ── Arquivos ───────────────────────────────────────────────────────────────

class Arquivos(TemplateView):
    template_name = 'blog/arquivos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        qs = Arquivo.objects.order_by('-data_modificacao')
        if query:
            qs = qs.filter(Q(titulo__icontains=query) | Q(descricao__icontains=query))
        context['arquivos'] = qs
        context['query'] = query
        return context


class PesquisarArquivo(Arquivos):
    pass


# ── Biblioteca ─────────────────────────────────────────────────────────────

class Biblioteca(TemplateView):
    template_name = 'blog/biblioteca.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        qs = Livro.objects.order_by('-data_modificacao')
        if query:
            qs = qs.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
        context['livros'] = qs
        context['categorias'] = CategoriaArquivo.objects.order_by('categoria')
        context['query'] = query
        return context


class PesquisarLivro(Biblioteca):
    pass


# ── Videoaulas ─────────────────────────────────────────────────────────────

ANOS_MAP = {
    '0Ano': 'Educação Infantil',
    '1Ano': '1º Ano', '2Ano': '2º Ano', '3Ano': '3º Ano',
    '4Ano': '4º Ano', '5Ano': '5º Ano', '6Ano': '6º Ano',
    '7Ano': '7º Ano', '8Ano': '8º Ano', '9Ano': '9º Ano',
}


class Eventos(LoginRequiredMixin, TemplateView):
    template_name = 'blog/tutoriais.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        qs = Video.objects.order_by('-data_atualizada')
        if query:
            qs = qs.filter(Q(titulo__icontains=query) | Q(materia__icontains=query))
        context['videos'] = qs
        context['query'] = query
        context['anos'] = [
            {'slug': k, 'label': v}
            for k, v in ANOS_MAP.items()
            if k != '0Ano'
        ]
        return context


class PesquisarVideo(Eventos):
    pass


class AnoMateria(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'blog/tutoriais_ano.html'
    context_object_name = 'videos'

    def get_queryset(self):
        descricao = ANOS_MAP.get(self.kwargs['ano'], 'Educação Infantil')
        ano = Ano.objects.filter(descricao=descricao).first()
        return Video.objects.filter(ano=ano, sigla=self.kwargs['sigla'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ano_label'] = ANOS_MAP.get(self.kwargs['ano'], '')
        context['sigla'] = self.kwargs['sigla']
        return context
