from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from .traduzir import converter
from .models import UnidadeEscolar, EnderecoEscolar
from ..aluno.models import Aluno
from ..core.models import Usuario
from ..frequencia.models import Frequencia, FrequenciaAluno
from ..sala.models import Sala
from .traduzir import converter
from .gerarPlanilhaFrequencia import criarFrequencia, dias_mes, presentesDia, dias, percentual


class Painel(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_administrator:
            escolas = UnidadeEscolar.objects.all()
            context['escolas'] = escolas
            return context
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)
            context['escola'] = escola
            return context


class PainelPlanilha(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle01.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dia = self.request.GET.get("data")
        data = datetime.strptime(dia, '%d/%m/%Y')
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        manha = Sala.objects.filter(turno='manha', escola=escola)
        tarde = Sala.objects.filter(turno='tarde', escola=escola)
        integral = Sala.objects.filter(turno='integral', escola=escola)

        fre_manha = []
        for sala in manha:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data)
                percentual(frequencias=freq, freq=frequence)
                fre_manha.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data, presentes=0)
                fre_manha.append(frequence)

        fre_tarde = []
        for sala in tarde:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data)
                percentual(frequencias=freq, freq=frequence)
                fre_tarde.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data, presentes=0)
                fre_tarde.append(frequence)

        fre_integral = []
        for sala in integral:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data)
                percentual(frequencias=freq, freq=frequence)
                fre_integral.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data, presentes=0)
                fre_integral.append(frequence)

        context['escola'] = escola
        context['manha'] = fre_manha
        context['tarde'] = fre_tarde
        context['integral'] = fre_integral
        context['data'] = data.date()
        context['escola'] = escola
        return context


class PainelPlanilha00(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle01.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dia = self.kwargs['data']
        x = dia.replace("-", "/")
        data_e = datetime.strptime(x, '%Y/%m/%d')
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        manha = Sala.objects.filter(turno='manha', escola=escola)
        tarde = Sala.objects.filter(turno='tarde', escola=escola)
        integral = Sala.objects.filter(turno='integral', escola=escola)
        fre_manha = []
        for sala in manha:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data_e, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data_e)
                percentual(frequencias=freq, freq=frequence)
                fre_manha.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data_e, presentes=0)
                fre_manha.append(frequence)

        fre_tarde = []
        for sala in tarde:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data_e, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data_e)
                percentual(frequencias=freq, freq=frequence)
                fre_tarde.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data_e, presentes=0)
                fre_tarde.append(frequence)

        fre_integral = []
        for sala in integral:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data_e, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data_e)
                percentual(frequencias=freq, freq=frequence)
                fre_integral.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data_e, presentes=0)
                fre_integral.append(frequence)

        context['escola'] = escola
        context['manha'] = fre_manha
        context['tarde'] = fre_tarde
        context['integral'] = fre_integral
        context['data'] = data_e.date()
        context['escola'] = escola
        return context


class PainelEscola(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
        salas = Sala.objects.filter(escola=escola).order_by('ano')
        ano = datetime.date.today().year
        mes = datetime.date.today().month
        mes_atual = dias_mes(mes=mes, ano=ano)
        m = mes_atual[0].strftime('%m')
        m1 = converter(int(m))
        presentes = presentesDia(mes_atual, salas)
        context['escola'] = escola
        context['salas'] = salas
        context['mes'] = dias(mes_atual)
        context['mes_atual'] = m1
        context['alunos'] = presentes
        return context


class EditarEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnidadeEscolar
    fields = ('nome_escola', 'inep', 'cnpj', 'telefone', 'logo_escola')
    success_message = 'Informações da instituição atualizadas'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_object(self, queryset=None):
        return UnidadeEscolar.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarUsuario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações do usuário atualizadas'
    template_name = 'escola/editarusuario_form.html'
    success_url = reverse_lazy('escola:painel_escola')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context


class EditarEndereco(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EnderecoEscolar
    fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')
    template_name = 'escola/editarendereco_form.html'
    success_message = 'Endereço atualizado com sucesso!'
    success_url = reverse_lazy('escola:painel_escola')

    def get_object(self, queryset=None):
        return EnderecoEscolar.objects.get(endereco=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(pk=self.request.user)
        context['escola'] = escola
        return context
