from django.shortcuts import render

# Create your views here.

def error_404(request, exception=None):
    return render(request, 'erros/404.html')

def error_500(request, exception=None):
    return render(request, 'erros/500.html')


def error_403(request, exception=None):
    return render(request, 'erros/403.html')


def error_400(request, exception=None):
    return render(request, 'erros/400.html')