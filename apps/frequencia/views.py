import calendar
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory, formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..sala.serializers import AlunoSerializer
from .serializers import FrequenciaSerializer, FrequenciaAlunoSerializer, FrequenciaBlocoSerializer, RegistroSerializer, \
    RelatorioSerializer, PeriodoSerializer
from ..escola.forms import FiltroMesForm
from django.views.generic import UpdateView, CreateView, ListView, DeleteView, TemplateView, FormView
from datetime import datetime
from .forms import FrequenciaAlunoForm, RegistroForm, RelatorioForm, RegistroUpdateForm, FrequenciaForm

from ..aluno.models import Aluno
from ..escola.models import UnidadeEscolar
from ..escola.traduzir import converter
from ..funcionario.models import Professor
from ..sala.models import Sala
from .models import Frequencia, FrequenciaAluno, Registro, Relatorio, Periodo
from django.core.serializers.json import DjangoJSONEncoder
import json



class RegistroMesesSalas(LoginRequiredMixin, FormView):
    template_name = 'frequencia/meses_salas.html'
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
        escola = get_object_or_404(UnidadeEscolar, pk=self.request.user)
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


class RelatorioAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatorio adicionado com sucesso!'
    template_name = 'frequencia/relatorio_add.html'

    def get_success_url(self):
        return reverse('funcionario:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo, 'slug':self.object.aluno.sala.escola.slug})

    def form_valid(self, form):
        relatorio = form.save(commit=False)
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        relatorio.aluno = aluno
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        relatorio.professor = professor.professor_nome
        periodo = Periodo.objects.get(periodo=self.kwargs['bimestre'])
        relatorio.periodo = periodo
        relatorio.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        professor = Professor.objects.get(usuario_ptr=self.request.user)
        contexto['professor'] = professor
        contexto['escola'] = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        contexto['aluno'] = get_object_or_404(Aluno, pk=self.kwargs['pk'])
        contexto['bimestre'] = self.kwargs['bimestre']
        return contexto


class RelatorioUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Relatorio
    form_class = RelatorioForm
    success_message = 'Relatório alterado com sucesso!'
    template_name = 'frequencia/relatorio_up.html'
    context_object_name = 'relatorio'


    def get_success_url(self):
        return reverse('funcionario:alunos_relatorios',
                       kwargs={'pk': self.object.aluno.sala.pk, 'bimestre': self.object.periodo,
                               'slug': self.object.aluno.sala.escola.slug})

    def form_valid(self, form):
        relatorio = form.save(commit=False)
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        relatorio.professor = professor.professor_nome
        relatorio.save()
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, usuario_ptr=self.request.user)
        contexto['professor'] = professor
        contexto['escola'] = get_object_or_404(UnidadeEscolar, pk=professor.escola.pk)
        contexto['sala'] = get_object_or_404(Sala, pk=self.object.aluno.sala.pk)
        return contexto


class ProfessorRegistroMesesSalas(LoginRequiredMixin, FormView):
    template_name = 'frequencia/prof_meses_salas.html'
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
        sala = get_object_or_404(Sala, id=self.kwargs['sala_id'])
        escola = get_object_or_404(UnidadeEscolar, pk=sala.escola.pk)
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
            ).order_by('data')
            context['registros'] = registros

        return context


class RegistroAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Registro
    form_class = RegistroForm
    success_message = 'Registro adicionado com sucesso!'
    template_name = 'frequencia/registro_add.html'

    def get_success_url(self):
        return reverse('frequencia:prof_relatorio_meses', kwargs={'sala_id': self.kwargs['pk']})

    def form_valid(self, form):
        registro = form.save(commit=False)
        sala = Sala.objects.get(pk=self.kwargs['pk'])
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        registro.professor = professor.professor_nome
        registro.sala = sala
        registro.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.is_professor:
            professor = Professor.objects.get(usuario_ptr=self.request.user)
            escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        else:
            escola = UnidadeEscolar.objects.get(pk=self.request.user)

        sala = Sala.objects.get(pk=self.kwargs['pk'])
        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['sala'] = sala
        return contexto


class RegistroUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Registro
    form_class = RegistroUpdateForm
    success_message = 'Registro alterado com sucesso!'
    template_name = 'frequencia/registro_up.html'

    def get_success_url(self):
        return reverse_lazy('frequencia:prof_relatorio_meses', kwargs={'sala_id': self.object.sala.pk})

    def form_valid(self, form):
        registro = form.save(commit=False)
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        registro.professor = professor.professor_nome
        registro.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        professor = Professor.objects.get(usuario_ptr=self.request.user)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        sala = Sala.objects.get(pk=self.object.sala.pk)

        contexto['professor'] = professor
        contexto['escola'] = escola
        contexto['sala'] = sala
        return contexto


class DeletarRegistro(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Registro
    success_message = 'Registro removido com sucesso!'

    def get_object(self, queryset=None):
        return Registro.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('frequencia:prof_relatorio_meses', kwargs={'sala_id': self.object.sala.pk})


class FrequenciaMes(LoginRequiredMixin, TemplateView):
    template_name = 'frequencia/frequencia_mes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = get_object_or_404(Professor, usuario_ptr=self.request.user)
        sala = get_object_or_404(Sala, pk=self.kwargs['pk'])

        ano = int(self.request.GET.get('ano', datetime.now().year))
        mes = int(self.request.GET.get('mes', datetime.now().month))

        frequencias = FrequenciaAluno.objects.filter(
            aluno__sala=sala,
            data__year=ano,
            data__month=mes
        ).values_list('data', flat=True)

        datas_dict = {data.strftime('%Y-%m-%d'): True for data in frequencias}

        context.update({
            'professor': professor,
            'escola': professor.escola,
            'sala': sala,
            'mes': mes,
            'ano': ano,
            'mes_nome': [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ][mes - 1],
            'frequencias_json': json.dumps(datas_dict),
        })

        return context


def atualizar_frequencia_diaria(request, cal, sala_id):
    data = datetime.strptime(cal, '%Y-%m-%d')

    if data.weekday() in [5, 6]:  # fim de semana
        return HttpResponse("Frequência não permitida aos finais de semana.", status=403)

    sala = get_object_or_404(Sala, pk=sala_id)
    alunos = Aluno.objects.filter(sala=sala)

    FrequenciaFormSet = formset_factory(FrequenciaForm, extra=0)

    if request.method == 'POST':
        formset = FrequenciaFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                aluno_id = form.cleaned_data.get('aluno_id')
                presente = form.cleaned_data.get('presente', False)
                observacao = form.cleaned_data.get('observacao', '')

                try:
                    frequencia = FrequenciaAluno.objects.get(aluno_id=aluno_id, data=data)
                    frequencia.presente = presente
                    frequencia.observacao = observacao
                    frequencia.save()
                except FrequenciaAluno.DoesNotExist:
                    continue  # ignora se não existir

            return HttpResponseRedirect(reverse_lazy('frequencia:frequencia_mes', kwargs={'pk': sala.pk}))
    else:
        initial_data = []
        for aluno in alunos:
            try:
                freq = FrequenciaAluno.objects.get(aluno=aluno, data=data)
                initial_data.append({
                    'aluno_id': aluno.id,
                    'nome': aluno.nome,
                    'presente': freq.presente,
                    'observacao': freq.observacao,
                })
            except FrequenciaAluno.DoesNotExist:
                # Se não existe, pula (não preenche o formset)
                continue

        formset = FrequenciaFormSet(initial=initial_data)

    return render(request, 'frequencia/up_frequencia_aluno.html', {
        'formset': formset,
        'sala': sala,
        'data': data.date(),
    })


def frequencia_diaria(request, cal, sala_id):
    data = datetime.strptime(cal, '%Y-%m-%d')

    if data.weekday() in [5, 6]:  # fim de semana
        return HttpResponse("Frequência não permitida aos finais de semana.", status=403)

    sala = get_object_or_404(Sala, pk=sala_id)
    alunos = Aluno.objects.filter(sala=sala)

    FrequenciaFormSet = formset_factory(FrequenciaForm, extra=0)

    if request.method == 'POST':
        formset = FrequenciaFormSet(request.POST)
        if formset.is_valid():
            total_presentes = 0  # contador de alunos presentes

            for form in formset:
                aluno_id = form.cleaned_data.get('aluno_id')
                presente = form.cleaned_data.get('presente', False)
                observacao = form.cleaned_data.get('observacao', '')

                aluno = get_object_or_404(Aluno, pk=aluno_id)

                fa, created = FrequenciaAluno.objects.update_or_create(
                    aluno=aluno,
                    data=data,
                    defaults={'presente': presente, 'observacao': observacao}
                )

                if presente:
                    total_presentes += 1

            # Criar ou atualizar a Frequencia da sala
            Frequencia.objects.update_or_create(
                sala=sala,
                data=data,
                defaults={
                    'presentes': total_presentes,
                    'status': True  # ou False dependendo do seu critério
                }
            )

            return HttpResponseRedirect(reverse_lazy('frequencia:frequencia_mes', kwargs={'pk': sala.pk}))
    else:
        # Prepare dados iniciais incluindo frequências já existentes
        initial_data = []
        for aluno in alunos:
            try:
                freq = FrequenciaAluno.objects.get(aluno=aluno, data=data)
                initial_data.append({
                    'aluno_id': aluno.id,
                    'nome': aluno.nome,
                    'presente': freq.presente,
                    'observacao': freq.observacao,
                })
            except FrequenciaAluno.DoesNotExist:
                initial_data.append({
                    'aluno_id': aluno.id,
                    'nome': aluno.nome,
                    'presente': True,
                    'observacao': '',
                })

        formset = FrequenciaFormSet(initial=initial_data)

    return render(request, 'frequencia/frequencia_aluno.html', {
        'formset': formset,
        'sala': sala,
        'data': data.date(),
    })



#### APIs ####
class FrequenciaViewSet(viewsets.ModelViewSet):
    queryset = Frequencia.objects.all()
    serializer_class = FrequenciaSerializer

    # 1. Frequências de uma sala por mês
    @action(detail=False, methods=['get'], url_path='sala/(?P<sala_id>[^/.]+)')
    def frequencias_sala_mes(self, request, sala_id=None):
        mes = request.query_params.get('mes')
        if not mes:
            return Response({"error": "Parâmetro 'mes' é obrigatório"}, status=400)
        try:
            ano, mes_int = map(int, mes.split('-'))
        except ValueError:
            return Response({"error": "Formato de 'mes' inválido"}, status=400)

        frequencias = Frequencia.objects.filter(
            sala_id=sala_id,
            data__year=ano,
            data__month=mes_int,
            status=True
        )
        dias = [{"data": f.data.strftime('%Y-%m-%d'), "frequencia_registrada": f.status} for f in frequencias]
        return Response(dias)

    # 2. Criar ou atualizar bloco de frequência
    @action(detail=False, methods=['post'])
    def criar_bloco(self, request):
        serializer = FrequenciaBlocoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sala_id = serializer.validated_data['sala_id']
        data_frequencia = serializer.validated_data['data']
        alunos_data = serializer.validated_data['frequencias_alunos']

        # Cria ou atualiza frequência da sala
        sala_frequencia, created = Frequencia.objects.get_or_create(
            sala_id=sala_id,
            data=data_frequencia,
            defaults={
                "presentes": sum(a['presente'] for a in alunos_data),
                "status": True
            }
        )
        if not created:
            sala_frequencia.presentes = sum(a['presente'] for a in alunos_data)
            sala_frequencia.status = True
            sala_frequencia.save()

        # Cria ou atualiza frequência de cada aluno
        for aluno_data in alunos_data:
            FrequenciaAluno.objects.update_or_create(
                aluno_id=aluno_data['aluno'],
                data=data_frequencia,
                defaults={
                    "presente": aluno_data['presente'],
                    "observacao": aluno_data.get('observacao', '')
                }
            )

        return Response({"success": True})

    # 3. Atualizar frequência de um aluno específico
    @action(detail=False, methods=['patch'], url_path='aluno/(?P<aluno_id>[^/.]+)/(?P<data>[^/.]+)')
    def atualizar_aluno(self, request, aluno_id=None, data=None):
        frequencia_aluno = get_object_or_404(FrequenciaAluno, aluno_id=aluno_id, data=data)
        serializer = FrequenciaAlunoSerializer(frequencia_aluno, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 4. Buscar frequências de todos os alunos de uma sala em uma data específica
    @action(detail=False, methods=['get'], url_path='aluno-frequencia/(?P<sala_id>[^/.]+)')
    def frequencias_por_data(self, request, sala_id=None):
        data_str = request.query_params.get('data')
        if not data_str:
            return Response({"error": "Parâmetro 'data' é obrigatório"}, status=400)
        try:
            from datetime import datetime
            data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de 'data' inválido, use YYYY-MM-DD"}, status=400)

        frequencias = FrequenciaAluno.objects.filter(
            aluno__sala_id=sala_id,
            data=data_obj
        )

        resultado = [
            {
                "id": f.id,
                "aluno": f.aluno.id,
                "presente": f.presente,
                "observacao": f.observacao
            } for f in frequencias
        ]
        return Response(resultado)


class FrequenciaAlunoViewSet(viewsets.ModelViewSet):
    queryset = FrequenciaAluno.objects.all()
    serializer_class = FrequenciaAlunoSerializer

    @action(detail=False, methods=['patch'], url_path='aluno/(?P<aluno_id>[^/.]+)/(?P<data>[^/.]+)')
    def atualizar_aluno(self, request, aluno_id=None, data=None):
        """Atualiza a frequência de um aluno específico em uma data"""
        frequencia_aluno = get_object_or_404(FrequenciaAluno, aluno_id=aluno_id, data=data)
        serializer = self.get_serializer(frequencia_aluno, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AlunosSalaFrequenciaViewSet(viewsets.ModelViewSet):
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        sala_id = self.kwargs.get("sala_pk")
        if not sala_id:
            raise ValidationError("ID da sala é obrigatório.")
        return Aluno.objects.filter(sala_id=sala_id).order_by("nome")

    def perform_create(self, serializer):
        sala_id = self.kwargs.get("sala_pk")
        try:
            sala = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            raise ValidationError("Sala não encontrada.")
        serializer.save(sala=sala)


class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all().order_by("-data")
    serializer_class = RegistroSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sala_id = self.request.query_params.get("sala")
        data_inicio = self.request.query_params.get("data__gte")
        data_fim = self.request.query_params.get("data__lte")

        if sala_id:
            queryset = queryset.filter(sala_id=sala_id)

        if data_inicio:
            queryset = queryset.filter(data__gte=parse_date(data_inicio))
        if data_fim:
            queryset = queryset.filter(data__lte=parse_date(data_fim))

        return queryset


class LargePagination(PageNumberPagination):
    page_size = 100


class RelatorioViewSet(viewsets.ModelViewSet):
    queryset = Relatorio.objects.all().order_by("-data_relatorio")
    serializer_class = RelatorioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargePagination

    def perform_create(self, serializer):
        periodo_id = self.request.data.get("periodo")
        periodo = get_object_or_404(Periodo, id=periodo_id)
        professor = Professor.objects.get(id=self.request.user.id)
        serializer.save(professor=professor.professor_nome, periodo=periodo)

    def update(self, request, *args, **kwargs):
        relatorio_obj = self.get_object()
        relatorio_texto = request.data.get("relatorio")

        if relatorio_texto is not None:
            relatorio_obj.relatorio = relatorio_texto
            relatorio_obj.save()
            serializer = self.get_serializer(relatorio_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Campo 'relatorio' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )


class PeriodoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Periodo.objects.all().order_by('periodo')
    serializer_class = PeriodoSerializer
    permission_classes = [IsAuthenticated]
