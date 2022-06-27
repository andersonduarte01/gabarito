from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'core/index.html'


class Base(TemplateView):
    template_name = 'temp_base/adm.html'
