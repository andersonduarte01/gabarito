from django.shortcuts import render
from unidecode import unidecode
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from ..blog.models import Blog, Categoria
from ..escola.models import UnidadeEscolar


class Noticias(ListView):
    model = Blog
    template_name = 'blog/blog.html'
    context_object_name = 'noticias'

    def get_queryset(self):
        return Blog.objects.filter().order_by('-data')


class Noticia(DetailView):
    model = Blog
    template_name = 'blog/noticia.html'
    context_object_name = 'noticia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temas = Categoria.objects.all()
        noticias = Blog.objects.filter().order_by('-data')
        recentes = noticias[:2]
        context['temas'] = temas
        context['recentes'] = recentes
        return context


class AddNoticia(CreateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = '/blog/'

    def form_valid(self, form):
        noticia = form.save(commit=False)
        x = noticia.titulo.replace(' ', '-')
        print(x)
        notice = unidecode(x)
        print(notice)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        noticia.autor = escola
        noticia.slug = notice.lower()
        noticia.save()
        return super().form_valid(form)


class EditNoticia(UpdateView):
    model = Blog
    fields = ('titulo', 'imagem', 'conteudo', 'categoria')
    template_name = 'blog/add_noticia.html'
    success_url = '/blog/'

