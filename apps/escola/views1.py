from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from datetime import date
from datetime import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView, UpdateView, ListView, RedirectView, FormView

from .forms import FiltroMesForm
from .models import UnidadeEscolar, EnderecoEscolar, AnoLetivo
from ..aluno.models import Aluno
from ..avaliacao.correcao import alunos_prova
from ..avaliacao.models import Avaliacao, Gabarito
from ..core.models import Usuario
from ..frequencia.models import Frequencia, FrequenciaAluno, Registro, Periodo, Relatorio
from ..funcionario.models import Professor
from ..sala.models import Sala
from .traduzir import converter
from .gerarPlanilhaFrequencia import dias_mes, presentesDia, dias, percentual

class Redireciona(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        user = self.request.user
        print(user)
        if user.is_administrator:
            print('Adm')
            return reverse_lazy('escola:painel_adm')
        elif user.is_professor:
            print('Prof')
            return reverse_lazy('funcionario:dash_professor')
        elif user.is_aluno:
            print('Aluno')
            return reverse_lazy('aluno:dash_aluno')
        elif user.is_funcionario:
            print('func')
            return reverse_lazy('funcionario:dash_funcionario')
        print('Escola')
        return reverse_lazy('escola:dash_escola')


class DashAdm(LoginRequiredMixin, TemplateView):
    template_name = 'escola/administrador_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escolas = UnidadeEscolar.objects.all()
        context['escolas'] = escolas
        return context


class DashEscola(LoginRequiredMixin, TemplateView):
    template_name = 'escola/escola_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        ano_corrente = AnoLetivo.objects.get(corrente=True)
        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        return context


class AdmUnidEscolar(LoginRequiredMixin, TemplateView):
    template_name = 'escola/adm_unidade_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        ano_corrente = AnoLetivo.objects.get(corrente=True)
        salas = Sala.objects.filter(escola=escola, ano_letivo=ano_corrente).order_by('ano')
        context['escola'] = escola
        context['salas'] = salas
        context['data'] = now()
        return context


class AdmUnidAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/adm_unidade_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        return Aluno.objects.filter(sala_id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, id=self.kwargs['id'])
        context['escola'] = escola
        context['sala'] = sala
        return context


class RegistroPorMesView(FormView):
    template_name = 'escola/adm_registros_dash.html'
    form_class = FiltroMesForm
    registros_filtrados = None  # Adiciona um atributo para armazenar os registros

    def form_valid(self, form):
        mes = int(form.cleaned_data['mes'])
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        self.registros_filtrados = Registro.objects.filter(
            sala=sala,
            data__month=mes,
            data__year=now().year
        )
        context = self.get_context_data(form=form, registros=self.registros_filtrados)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        context['escola'] = escola
        context['form'] = context.get('form') or self.form_class(initial={'mes': now().month})
        context['sala'] = sala

        if self.registros_filtrados is not None:
            context['registros'] = self.registros_filtrados
        else:
            registros = Registro.objects.filter(
                sala=sala,
                data__month=now().month,
                data__year=now().year
            )
            context['registros'] = registros

        return context
    
    
class AdmListaAlunosrelatorios(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/adm_unidade_alunos_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        alunos_relatorios = []
        for aluno in alunos:
            aluno_relatorio = []
            aluno_relatorio.append(aluno)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorio = Relatorio.objects.filter(aluno=aluno, periodo=periodo, data_relatorio__year=datetime.now().year).firts()
                aluno_relatorio.append(relatorio)
            except:
                relatorio = None
                aluno_relatorio.append(relatorio)

            alunos_relatorios.append(aluno_relatorio)

        context['bimestre'] = self.kwargs['bimestre']
        context['sala'] = sala
        context['alunos'] = alunos_relatorios
        context['escola'] = escola
        return context


class AdmListaEscolaProfessores(LoginRequiredMixin, ListView):
    model = Professor
    template_name = 'escola/escola_lista_professores_dash.html'
    context_object_name = 'professores'

    def get_queryset(self):
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        return Professor.objects.filter(escola=escola)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        context['escola'] = escola
        return context


class UniEditarEscola(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnidadeEscolar
    fields = ('nome_escola', 'inep', 'cnpj', 'telefone', 'logo_escola')
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarescolar_form.html'
    success_url = reverse_lazy('escola:dash_escola')

    def get_object(self, queryset=None):
        return get_object_or_404(UnidadeEscolar, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.get_object()
        context['escola'] = escola
        return context


class UniEditarEndereco(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EnderecoEscolar
    fields = ('rua', 'numero', 'complemento', 'bairro', 'cep', 'cidade', 'estado')
    template_name = 'escola/editarendereco_form.html'
    success_message = 'Endereço atualizado com sucesso!'
    success_url = reverse_lazy('escola:dash_escola')

    def get_object(self, queryset=None):
        return get_object_or_404(EnderecoEscolar, endereco=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.get_object()
        context['escola'] = escola
        return context


class UniEditarUsuario(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    fields = ('email', 'nome')
    success_message = 'Informações atualizadas com sucesso!'
    template_name = 'escola/editarusuario_form.html'
    success_url = reverse_lazy('escola:dash_escola')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
        context['escola'] = escola
        return context


##ANTIGOS##

class Painel(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_administrator:
            escolas = UnidadeEscolar.objects.all()
            context['escolas'] = escolas
            return context
        elif self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            context['escola'] = UnidadeEscolar.objects.get(pk=professor.escola.pk)
            context['professor'] = professor
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
        professor = ''
        escola = None
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        salas = Sala.objects.filter(escola=escola)

        fre_registros = []
        for sala in salas:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data)
                percentual(frequencias=freq, freq=frequence)
                fre_registros.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data, presentes=0)
                percentual(frequencias=freq, freq=frequence)
                fre_registros.append(frequence)

        context['salas'] = fre_registros
        context['data'] = data.date()
        context['escola'] = escola
        context['professor'] = professor
        return context


class PainelPlanilha00(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_controle01.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dia = self.kwargs['data']
        x = dia.replace("-", "/")
        data_e = datetime.strptime(x, '%Y/%m/%d')
        escola = None
        professor = None
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)
        salas = Sala.objects.filter(escola=escola)
        fre_registros = []
        for sala in salas:
            alunos = Aluno.objects.filter(sala=sala)
            freq = FrequenciaAluno.objects.filter(data=data_e, aluno__in=alunos).order_by()
            try:
                frequence = Frequencia.objects.get(sala=sala, data=data_e)
                percentual(frequencias=freq, freq=frequence)
                fre_registros.append(frequence)
            except:
                frequence = Frequencia.objects.create(sala=sala, data=data_e, presentes=0)
                percentual(frequencias=freq, freq=frequence)
                fre_registros.append(frequence)

        context['escola'] = escola
        context['salas'] = fre_registros
        context['data'] = data_e.date()
        context['professor'] = professor
        return context


class PainelEscola(LoginRequiredMixin, TemplateView):
    template_name = 'escola/painel_escola.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = UnidadeEscolar.objects.get(slug=self.kwargs['slug'])
        salas = Sala.objects.filter(escola=escola).order_by('ano')
        ano = date.today().year
        mes = date.today().month
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









### Administrador ###


class ListaEscolaSalas(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'escola/escola_salas.html'
    context_object_name = 'salas'

    def get_queryset(self):
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        return Sala.objects.filter(escola=escola).order_by('ano')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        context['escola'] = escola
        return context


class PesquisarEscola(ListView):
    model = UnidadeEscolar
    template_name = 'escola/escola_resultados.html'
    context_object_name = 'escolas'
    def get_queryset(self):
        query = self.request.GET.get("q")
        escolas = UnidadeEscolar.objects.filter(Q(nome_escola__icontains=query))
        return escolas


class ListaEscolaSalaAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/escola_sala_alunos.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['id'])
        return Aluno.objects.filter(sala=sala).order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        sala = Sala.objects.get(pk=self.kwargs['id'])
        context['escola'] = escola
        context['sala'] = sala
        return context



class EscolaListAvaliacoes(LoginRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'escola/escola_avaliacoes.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        return escola.avaliacao_escola.all().filter(data_encerramento__gte=datetime.now().date())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        context['escola'] = escola
        return context


class EscolaAvaliacaoListSalas(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'escola/escola_avaliacao_salas.html'
    context_object_name = 'salas'

    def get_queryset(self):
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        avaliacao = Avaliacao.objects.get(id=self.kwargs['id_avaliacao'])
        return Sala.objects.filter(escola=escola, ano=avaliacao.ano)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        avaliacao = Avaliacao.objects.get(id=self.kwargs['id_avaliacao'])
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        return context


class EscolaAvaliacaoAlunos(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/escola_avaliacao_alunos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avaliacao = Avaliacao.objects.get(pk=self.kwargs['avaliacao_id'])
        sala = Sala.objects.get(pk=self.kwargs['sala_id'])
        alunos = Aluno.objects.filter(sala=self.kwargs['sala_id'])
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])
        gabaritos, alunos_avaliar, questoes = alunos_prova(avaliacao=avaliacao, alunos=alunos)
        context['escola'] = escola
        context['avaliacao'] = avaliacao
        context['alunos'] = alunos_avaliar
        context['sala'] = sala
        context['questoes'] = questoes
        context['gabaritos'] = gabaritos
        return context

### outros ####


class EscolaRegistroMesesSalas(LoginRequiredMixin, ListView):
    template_name = 'escola/escola_meses_salas.html'
    context_object_name = 'meses'

    def get_queryset(self):
        nome_meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
            4: 'Abril', 5: 'Maio',  6: 'Junho', 7: 'Julho',
            8: 'Agosto', 9: 'Setembro', 10: 'Outubro',
            11: 'Novembro', 12: 'Dezembro'
        }

        registros_com_mes = Registro.objects.annotate(mes_registro=ExtractMonth('data'))
        meses_unicos = registros_com_mes.values_list('mes_registro', flat=True).distinct()
        nomes_e_numeros_meses = [(mes, nome_meses[mes]) for mes in meses_unicos]
        nomes_e_numeros_meses = sorted(nomes_e_numeros_meses, key=lambda x: x[0])
        return nomes_e_numeros_meses

    def get_context_data(self, *, object_list=None, **kwargs):
        contexto = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        salas = Sala.objects.filter(escola=escola)

        contexto['escola'] = escola
        contexto['salas'] = salas
        return contexto


class EscolaRegistroMesSala(LoginRequiredMixin, ListView):
    template_name = 'escola/escola_mes_sala.html'
    context_object_name = 'mes'

    def get_queryset(self):
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        return Registro.objects.filter(data__month=self.kwargs['mes'], sala=sala).order_by('data')

    def get_context_data(self, *, object_list=None, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = 'vazio'
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        sala = Sala.objects.get(pk=self.kwargs['pk'])

        contexto['escola'] = escola
        contexto['professor'] = professor
        contexto['sala'] = sala
        return contexto


class EscolaPainelRelatorios(LoginRequiredMixin, TemplateView):
    template_name = 'escola/escola_painel_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        salas = Sala.objects.filter(escola=escola)

        salas_relatorios = []
        for sala in salas:

            sala_relatorio = []

            sala_relatorio.append(sala)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorios = Relatorio.objects.filter(aluno__sala=sala, periodo=periodo).count()
                sala_relatorio.append(relatorios)
            except:
                relatorios = 0
                sala_relatorio.append(relatorios)

            salas_relatorios.append(sala_relatorio)

        context['salas'] = salas_relatorios
        context['texto_bimestre'] = self.kwargs['bimestre'].replace('_', ' ')
        context['bimestre'] = self.kwargs['bimestre']
        context['escola'] = escola
        return context


class EscolaListaAlunosrelatorios(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'escola/escola_alunos_relatorios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        alunos = Aluno.objects.filter(sala=sala).order_by('nome')
        periodo = get_object_or_404(Periodo,periodo=self.kwargs['bimestre'])
        escola = get_object_or_404(UnidadeEscolar, slug=self.kwargs['slug'])

        alunos_relatorios = []
        for aluno in alunos:
            aluno_relatorio = []
            aluno_relatorio.append(aluno)
            try:
                periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
                relatorio = Relatorio.objects.get(aluno=aluno, periodo=periodo)
                aluno_relatorio.append(relatorio)
            except:
                relatorio = None
                aluno_relatorio.append(relatorio)

            alunos_relatorios.append(aluno_relatorio)

        context['bimestre'] = self.kwargs['bimestre']
        context['sala'] = sala
        context['alunos'] = alunos_relatorios
        context['escola'] = escola
        return context


class EscolaRelatorio(LoginRequiredMixin, ListView):
    model = Relatorio
    template_name = 'escola/escola_relatorio.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        periodo = get_object_or_404(Periodo, periodo=self.kwargs['bimestre'])
        relatorio = get_object_or_404(Relatorio, aluno=aluno, periodo=periodo)
        escola = UnidadeEscolar.objects.get(pk=aluno.sala.escola.pk)

        contexto['escola'] = escola
        contexto['aluno'] = aluno
        contexto['relatorio'] = relatorio
        contexto['bimestre'] = self.kwargs['bimestre']
        return contexto
