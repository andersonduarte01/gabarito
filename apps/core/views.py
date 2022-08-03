from django.views.generic import TemplateView

from ..escola.models import UnidadeEscolar


class Index(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and (self.request.user.is_administrator is False):
            escola = UnidadeEscolar.objects.get(pk=self.request.user)
            context['school'] = escola
        return context




class Base(TemplateView):
    template_name = 'temp_base/adm.html'
