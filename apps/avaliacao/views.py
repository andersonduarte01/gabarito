from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import AvaliacaoForm, OpcaoRespostaForm, QuestaoForm
from .models import Avaliacao, OpcaoResposta, Questao
from .services import avaliacao_service


class _LeituraMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in ('DIRETOR', 'FUNCIONARIO', 'PROFESSOR'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class _EscritaMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in ('DIRETOR', 'FUNCIONARIO', 'PROFESSOR'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


class _DiretorMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo != 'DIRETOR':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def _ctx(self, request, **extra):
        return {'usuario': request.user, 'escola': request.escola, 'papel': request.papel, **extra}


def _turma_ids_professor(papel):
    try:
        from apps.turma.models import ProfessorMateriaTurma
        return list(
            ProfessorMateriaTurma.objects
            .filter(professor=papel.perfil_professor, ativo=True)
            .values_list('turma_id', flat=True)
        )
    except Exception:
        return []


class ListarAvaliacoesView(_LeituraMixin, View):
    template_name = 'avaliacao/lista.html'

    def get(self, request):
        escola = request.escola
        qs = (
            Avaliacao.objects
            .filter(escola=escola)
            .select_related('turma', 'materia', 'ano_letivo', 'periodo_letivo')
            .order_by('-data_aplicacao', '-criado_em')
        )

        # Calcula turma_ids uma única vez para professor
        turma_ids = _turma_ids_professor(request.papel) if request.papel.tipo == 'PROFESSOR' else None
        if turma_ids is not None:
            qs = qs.filter(turma_id__in=turma_ids)

        turma_id = request.GET.get('turma', '')
        tipo     = request.GET.get('tipo', '')
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        if tipo:
            qs = qs.filter(tipo=tipo)

        from apps.turma.models import Turma
        from .models import TipoAvaliacao
        if turma_ids is not None:
            turmas = Turma.objects.filter(pk__in=turma_ids).order_by('nome')
        else:
            turmas = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')

        return render(request, self.template_name, self._ctx(
            request,
            avaliacoes=qs,
            turmas=turmas,
            tipo_choices=TipoAvaliacao.choices,
            filtros={'turma': turma_id, 'tipo': tipo},
        ))


class CriarAvaliacaoView(_EscritaMixin, View):
    template_name = 'avaliacao/form_avaliacao.html'

    def _turma_ids(self, request):
        return _turma_ids_professor(request.papel) if request.papel.tipo == 'PROFESSOR' else None

    def get(self, request):
        form = AvaliacaoForm(escola=request.escola, turma_ids=self._turma_ids(request))
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = AvaliacaoForm(request.POST, escola=request.escola, turma_ids=self._turma_ids(request))
        if form.is_valid():
            cd = form.cleaned_data
            professor = cd.get('professor')
            if request.papel.tipo == 'PROFESSOR':
                try:
                    professor = request.papel.perfil_professor
                except Exception:
                    professor = None
            avaliacao = avaliacao_service.criar(request.escola, {
                'turma':          cd['turma'],
                'materia':        cd['materia'],
                'professor':      professor,
                'ano_letivo':     cd['ano_letivo'],
                'periodo_letivo': cd.get('periodo_letivo'),
                'titulo':         cd['titulo'],
                'tipo':           cd['tipo'],
                'modalidade':     cd['modalidade'],
                'data_aplicacao': cd.get('data_aplicacao'),
                'nota_maxima':    cd['nota_maxima'],
                'peso':           cd['peso'],
            })
            messages.success(request, 'Avaliação criada com sucesso.')
            return redirect('avaliacao:detalhe', pk=avaliacao.pk)
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))


class DetalheAvaliacaoView(_LeituraMixin, View):
    template_name = 'avaliacao/detalhe.html'

    def get(self, request, pk):
        avaliacao = get_object_or_404(
            Avaliacao.objects.select_related(
                'turma', 'materia', 'ano_letivo', 'periodo_letivo', 'professor__papel__vinculo__usuario',
            ).prefetch_related('questoes__opcoes'),
            pk=pk, escola=request.escola,
        )
        questao_form = QuestaoForm()
        opcao_form   = OpcaoRespostaForm()

        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=avaliacao.turma, ano_letivo=avaliacao.ano_letivo, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        notas      = {n.aluno_id: n for n in avaliacao.notas.select_related('aluno')}
        notas_list = [(mat, notas.get(mat.aluno_id)) for mat in matriculas]

        from .forms import TIPOS_COM_OPCOES
        return render(request, self.template_name, self._ctx(
            request,
            avaliacao=avaliacao,
            questao_form=questao_form,
            opcao_form=opcao_form,
            notas_list=notas_list,
            tipos_com_opcoes=TIPOS_COM_OPCOES,
        ))


class EditarAvaliacaoView(_EscritaMixin, View):
    template_name = 'avaliacao/form_avaliacao.html'

    def _get(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        return get_object_or_404(qs, pk=pk)

    def _turma_ids(self, request):
        return _turma_ids_professor(request.papel) if request.papel.tipo == 'PROFESSOR' else None

    def get(self, request, pk):
        avaliacao = self._get(request, pk)
        form = AvaliacaoForm(escola=request.escola, instance=avaliacao, turma_ids=self._turma_ids(request))
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, avaliacao=avaliacao,
        ))

    def post(self, request, pk):
        avaliacao = self._get(request, pk)
        form = AvaliacaoForm(request.POST, escola=request.escola, turma_ids=self._turma_ids(request))
        if form.is_valid():
            cd = form.cleaned_data
            professor = cd.get('professor')
            if request.papel.tipo == 'PROFESSOR':
                try:
                    professor = request.papel.perfil_professor
                except Exception:
                    professor = None
            avaliacao_service.editar(avaliacao, {
                'turma':          cd['turma'],
                'materia':        cd['materia'],
                'professor':      professor,
                'ano_letivo':     cd['ano_letivo'],
                'periodo_letivo': cd.get('periodo_letivo'),
                'titulo':         cd['titulo'],
                'tipo':           cd['tipo'],
                'modalidade':     cd['modalidade'],
                'data_aplicacao': cd.get('data_aplicacao'),
                'nota_maxima':    cd['nota_maxima'],
                'peso':           cd['peso'],
            })
            messages.success(request, 'Avaliação atualizada.')
            return redirect('avaliacao:detalhe', pk=avaliacao.pk)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, avaliacao=avaliacao,
        ))


class PublicarView(_EscritaMixin, View):
    def post(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        avaliacao_service.publicar(avaliacao)
        messages.success(request, 'Avaliação publicada.')
        return redirect('avaliacao:detalhe', pk=pk)


class DespublicarView(_EscritaMixin, View):
    def post(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        avaliacao_service.despublicar(avaliacao)
        messages.success(request, 'Avaliação despublicada.')
        return redirect('avaliacao:detalhe', pk=pk)


class EncerrarView(_EscritaMixin, View):
    def post(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        avaliacao_service.encerrar(avaliacao)
        messages.success(request, 'Avaliação encerrada.')
        return redirect('avaliacao:detalhe', pk=pk)


class AdicionarQuestaoView(_EscritaMixin, View):
    def post(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                avaliacao_service.adicionar_questao(avaliacao, form.cleaned_data)
                messages.success(request, 'Questão adicionada.')
            except Exception as exc:
                messages.error(request, f'Erro ao adicionar questão: {exc}')
        else:
            erros = '; '.join(
                f'{f}: {e[0]}' for f, e in form.errors.items()
            )
            messages.error(request, f'Dados inválidos — {erros}')
        return redirect('avaliacao:detalhe', pk=pk)


class RemoverQuestaoView(_EscritaMixin, View):
    def post(self, request, pk, questao_pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        questao   = get_object_or_404(Questao, pk=questao_pk, avaliacao=avaliacao)
        numero    = questao.numero
        avaliacao_service.remover_questao(questao)
        messages.success(request, f'Questão {numero} removida.')
        return redirect('avaliacao:detalhe', pk=pk)


class AdicionarOpcaoView(_EscritaMixin, View):
    def post(self, request, pk, questao_pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        questao   = get_object_or_404(Questao, pk=questao_pk, avaliacao=avaliacao)
        form = OpcaoRespostaForm(request.POST)
        if form.is_valid():
            try:
                avaliacao_service.adicionar_opcao(questao, form.cleaned_data)
                messages.success(request, 'Opção adicionada.')
            except Exception as exc:
                messages.error(request, f'Erro ao adicionar opção: {exc}')
        else:
            messages.error(request, 'Dados da opção inválidos.')
        return redirect('avaliacao:detalhe', pk=pk)


class RemoverOpcaoView(_EscritaMixin, View):
    def post(self, request, pk, questao_pk, opcao_pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(qs, pk=pk)
        questao   = get_object_or_404(Questao, pk=questao_pk, avaliacao=avaliacao)
        opcao     = get_object_or_404(OpcaoResposta, pk=opcao_pk, questao=questao)
        letra     = opcao.letra
        avaliacao_service.remover_opcao(opcao)
        messages.success(request, f'Opção {letra} removida.')
        return redirect('avaliacao:detalhe', pk=pk)


class ExportarPdfView(_LeituraMixin, View):
    def get(self, request, pk):
        from .services.pdf_service import gerar_pdf_avaliacao

        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        avaliacao = get_object_or_404(
            qs.select_related(
                'turma', 'materia', 'ano_letivo', 'periodo_letivo',
                'professor__papel__vinculo__usuario', 'escola',
            ).prefetch_related('questoes__opcoes'),
            pk=pk,
        )

        try:
            pdf = gerar_pdf_avaliacao(avaliacao, request.escola)
        except Exception as exc:
            return HttpResponse(f'Erro ao gerar PDF: {exc}', status=500)

        nome = avaliacao.titulo[:50].replace(' ', '-').lower()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="avaliacao-{nome}.pdf"'
        return response


class LancarNotasView(_EscritaMixin, View):
    template_name = 'avaliacao/lancar_notas.html'

    def _get_avaliacao(self, request, pk):
        qs = Avaliacao.objects.filter(escola=request.escola)
        if request.papel.tipo == 'PROFESSOR':
            qs = qs.filter(turma_id__in=_turma_ids_professor(request.papel))
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        avaliacao = self._get_avaliacao(request, pk)
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=avaliacao.turma, ano_letivo=avaliacao.ano_letivo, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        notas      = {n.aluno_id: n for n in avaliacao.notas.all()}
        notas_list = [(mat, notas.get(mat.aluno_id)) for mat in matriculas]
        return render(request, self.template_name, self._ctx(
            request, avaliacao=avaliacao, notas_list=notas_list,
        ))

    def post(self, request, pk):
        avaliacao = self._get_avaliacao(request, pk)
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=avaliacao.turma, ano_letivo=avaliacao.ano_letivo, ativo=True)
            .select_related('aluno')
        )
        entradas = []
        for mat in matriculas:
            aluno_id = mat.aluno_id
            ausente  = bool(request.POST.get(f'ausente_{aluno_id}'))
            obs      = request.POST.get(f'obs_{aluno_id}', '').strip()
            raw_nota = request.POST.get(f'nota_{aluno_id}', '').strip()
            nota = None
            if not ausente and raw_nota:
                try:
                    nota = Decimal(raw_nota.replace(',', '.'))
                    # Clampa no intervalo [0, nota_maxima]
                    nota = max(Decimal('0'), min(nota, avaliacao.nota_maxima))
                except InvalidOperation:
                    pass
            entradas.append({'aluno_id': aluno_id, 'nota': nota, 'ausente': ausente, 'observacao': obs})

        count = avaliacao_service.lancar_notas_em_massa(avaliacao, entradas)
        messages.success(request, f'{count} notas salvas.')
        return redirect('avaliacao:detalhe', pk=pk)
