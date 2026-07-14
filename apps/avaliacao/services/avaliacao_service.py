from decimal import Decimal

from django.db import transaction

from apps.avaliacao.models import (
    Avaliacao, NotaAluno, OpcaoResposta, Questao, RespostaAluno, TipoQuestao,
)


def criar(escola, dados: dict) -> Avaliacao:
    return Avaliacao.objects.create(escola=escola, **dados)


def editar(avaliacao: Avaliacao, dados: dict) -> Avaliacao:
    for campo, valor in dados.items():
        setattr(avaliacao, campo, valor)
    avaliacao.save()
    return avaliacao


def publicar(avaliacao: Avaliacao) -> None:
    from apps.avaliacao.models import StatusAvaliacao
    avaliacao.status = StatusAvaliacao.PUBLICADA
    avaliacao.save(update_fields=['status'])


def despublicar(avaliacao: Avaliacao) -> None:
    from apps.avaliacao.models import StatusAvaliacao
    avaliacao.status = StatusAvaliacao.RASCUNHO
    avaliacao.save(update_fields=['status'])


def encerrar(avaliacao: Avaliacao) -> None:
    from apps.avaliacao.models import StatusAvaliacao
    avaliacao.status = StatusAvaliacao.ENCERRADA
    avaliacao.save(update_fields=['status'])


@transaction.atomic
def adicionar_questao(avaliacao: Avaliacao, dados: dict) -> Questao:
    # ClearableFileInput retorna False quando o campo está vazio sem upload
    dados = {k: (None if v is False else v) for k, v in dados.items()}
    return Questao.objects.create(avaliacao=avaliacao, **dados)


def remover_questao(questao: Questao) -> None:
    questao.delete()


@transaction.atomic
def adicionar_opcao(questao: Questao, dados: dict) -> OpcaoResposta:
    # Apenas tipos de resposta única impõem "uma correta por vez"
    _tipos_unica = (
        TipoQuestao.MULTIPLA_ESCOLHA,
        TipoQuestao.VERDADEIRO_FALSO,
    )
    if dados.get('correta') and questao.tipo in _tipos_unica:
        questao.opcoes.filter(correta=True).update(correta=False)
    return OpcaoResposta.objects.create(questao=questao, **dados)


def remover_opcao(opcao: OpcaoResposta) -> None:
    opcao.delete()


@transaction.atomic
def lancar_nota_manual(avaliacao: Avaliacao, aluno, nota, ausente: bool = False, observacao: str = '') -> NotaAluno:
    # Garante que a nota não exceda o máximo definido
    if nota is not None:
        nota = max(Decimal('0'), min(nota, avaliacao.nota_maxima))

    nota_obj, _ = NotaAluno.objects.update_or_create(
        avaliacao=avaliacao, aluno=aluno,
        defaults={'nota': nota, 'ausente': ausente, 'observacao': observacao},
    )
    if avaliacao.periodo_letivo_id:
        from apps.boletim.services import boletim_service
        boletim_service.calcular_periodo(aluno, avaliacao.materia, avaliacao.periodo_letivo)
    return nota_obj


@transaction.atomic
def lancar_notas_em_massa(avaliacao: Avaliacao, entradas: list) -> int:
    """
    entradas: [{'aluno_id': pk, 'nota': Decimal|None, 'ausente': bool, 'observacao': str}]
    Retorna contagem de notas salvas.
    """
    from apps.aluno.models import Aluno
    count = 0
    alunos = {a.pk: a for a in Aluno.objects.filter(pk__in=[e['aluno_id'] for e in entradas])}
    for entrada in entradas:
        aluno = alunos.get(entrada['aluno_id'])
        if aluno is None:
            continue
        lancar_nota_manual(
            avaliacao=avaliacao,
            aluno=aluno,
            nota=entrada.get('nota'),
            ausente=bool(entrada.get('ausente')),
            observacao=entrada.get('observacao', ''),
        )
        count += 1
    return count
