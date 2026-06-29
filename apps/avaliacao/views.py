from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import AvaliacaoForm, OpcaoRespostaForm, QuestaoForm
from .models import Avaliacao, NotaAluno, OpcaoResposta, Questao
from .services import avaliacao_service


class _LeituraMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        papel = getattr(request, 'papel', None)
        if papel is None or papel.tipo not in ('DIRETOR', 'FUNCIONARIO'):
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
        turma_id  = request.GET.get('turma', '')
        tipo      = request.GET.get('tipo', '')
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        if tipo:
            qs = qs.filter(tipo=tipo)

        from apps.turma.models import Turma
        from .models import TipoAvaliacao
        turmas = Turma.objects.filter(escola=escola, ativo=True).order_by('nome')
        return render(request, self.template_name, self._ctx(
            request,
            avaliacoes=qs,
            turmas=turmas,
            tipo_choices=TipoAvaliacao.choices,
            filtros={'turma': turma_id, 'tipo': tipo},
        ))


class CriarAvaliacaoView(_DiretorMixin, View):
    template_name = 'avaliacao/form_avaliacao.html'

    def get(self, request):
        form = AvaliacaoForm(escola=request.escola)
        return render(request, self.template_name, self._ctx(request, form=form, editando=False))

    def post(self, request):
        form = AvaliacaoForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            avaliacao = avaliacao_service.criar(request.escola, {
                'turma':          cd['turma'],
                'materia':        cd['materia'],
                'professor':      cd.get('professor'),
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
        notas = {n.aluno_id: n for n in avaliacao.notas.all()}
        notas_list = [(mat, notas.get(mat.aluno_id)) for mat in matriculas]

        return render(request, self.template_name, self._ctx(
            request,
            avaliacao=avaliacao,
            questao_form=questao_form,
            opcao_form=opcao_form,
            notas_list=notas_list,
        ))


class EditarAvaliacaoView(_DiretorMixin, View):
    template_name = 'avaliacao/form_avaliacao.html'

    def _get(self, request, pk):
        return get_object_or_404(Avaliacao, pk=pk, escola=request.escola)

    def get(self, request, pk):
        avaliacao = self._get(request, pk)
        form = AvaliacaoForm(escola=request.escola, instance=avaliacao)
        return render(request, self.template_name, self._ctx(
            request, form=form, editando=True, avaliacao=avaliacao,
        ))

    def post(self, request, pk):
        avaliacao = self._get(request, pk)
        form = AvaliacaoForm(request.POST, escola=request.escola)
        if form.is_valid():
            cd = form.cleaned_data
            avaliacao_service.editar(avaliacao, {
                'turma':          cd['turma'],
                'materia':        cd['materia'],
                'professor':      cd.get('professor'),
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


class PublicarView(_DiretorMixin, View):
    def post(self, request, pk):
        avaliacao = get_object_or_404(Avaliacao, pk=pk, escola=request.escola)
        avaliacao_service.publicar(avaliacao)
        messages.success(request, 'Avaliação publicada.')
        return redirect('avaliacao:detalhe', pk=pk)


class DespublicarView(_DiretorMixin, View):
    def post(self, request, pk):
        avaliacao = get_object_or_404(Avaliacao, pk=pk, escola=request.escola)
        avaliacao_service.despublicar(avaliacao)
        messages.success(request, 'Avaliação despublicada.')
        return redirect('avaliacao:detalhe', pk=pk)


class AdicionarQuestaoView(_DiretorMixin, View):
    def post(self, request, pk):
        avaliacao = get_object_or_404(Avaliacao, pk=pk, escola=request.escola)
        form = QuestaoForm(request.POST)
        if form.is_valid():
            try:
                avaliacao_service.adicionar_questao(avaliacao, form.cleaned_data)
                messages.success(request, 'Questão adicionada.')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        else:
            messages.error(request, 'Dados da questão inválidos.')
        return redirect('avaliacao:detalhe', pk=pk)


class RemoverQuestaoView(_DiretorMixin, View):
    def post(self, request, pk, questao_pk):
        avaliacao = get_object_or_404(Avaliacao, pk=pk, escola=request.escola)
        questao   = get_object_or_404(Questao, pk=questao_pk, avaliacao=avaliacao)
        avaliacao_service.remover_questao(questao)
        messages.success(request, f'Questão {questao.numero} removida.')
        return redirect('avaliacao:detalhe', pk=pk)


class AdicionarOpcaoView(_DiretorMixin, View):
    def post(self, request, pk, questao_pk):
        avaliacao = get_object_or_404(Avaliacao, pk=pk, escola=request.escola)
        questao   = get_object_or_404(Questao, pk=questao_pk, avaliacao=avaliacao)
        form = OpcaoRespostaForm(request.POST)
        if form.is_valid():
            try:
                avaliacao_service.adicionar_opcao(questao, form.cleaned_data)
                messages.success(request, 'Opção adicionada.')
            except Exception as exc:
                messages.error(request, f'Erro: {exc}')
        else:
            messages.error(request, 'Dados da opção inválidos.')
        return redirect('avaliacao:detalhe', pk=pk)


class LancarNotasView(_DiretorMixin, View):
    template_name = 'avaliacao/lancar_notas.html'

    def _get_avaliacao(self, request, pk):
        return get_object_or_404(Avaliacao, pk=pk, escola=request.escola)

    def get(self, request, pk):
        avaliacao = self._get_avaliacao(request, pk)
        from apps.aluno.models import MatriculaTurma
        matriculas = (
            MatriculaTurma.objects
            .filter(turma=avaliacao.turma, ano_letivo=avaliacao.ano_letivo, ativo=True)
            .select_related('aluno')
            .order_by('aluno__nome_completo')
        )
        notas = {n.aluno_id: n for n in avaliacao.notas.all()}
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
                except InvalidOperation:
                    pass
            entradas.append({'aluno_id': aluno_id, 'nota': nota, 'ausente': ausente, 'observacao': obs})

        count = avaliacao_service.lancar_notas_em_massa(avaliacao, entradas)
        messages.success(request, f'{count} notas salvas.')
        return redirect('avaliacao:detalhe', pk=pk)
