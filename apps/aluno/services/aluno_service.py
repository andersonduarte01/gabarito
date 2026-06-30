from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.aluno.models import Aluno, MatriculaTurma, SituacaoMatricula


def _gerar_matricula(escola) -> str:
    ano = timezone.now().year
    ultimo = (
        Aluno.objects
        .filter(escola=escola, matricula__startswith=str(ano))
        .order_by('-matricula')
        .values_list('matricula', flat=True)
        .first()
    )
    if ultimo:
        try:
            seq = int(ultimo[4:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'{ano}{seq:04d}'


@transaction.atomic
def criar(escola, dados: dict) -> Aluno:
    turma      = dados.pop('turma', None)
    ano_letivo = dados.pop('ano_letivo', None)
    matricula  = _gerar_matricula(escola)
    aluno = Aluno.objects.create(escola=escola, matricula=matricula, **dados)
    if turma and ano_letivo:
        MatriculaTurma.objects.create(
            aluno=aluno,
            turma=turma,
            ano_letivo=ano_letivo,
            situacao=SituacaoMatricula.MATRICULADO,
        )
    return aluno


def editar(aluno: Aluno, dados: dict) -> Aluno:
    for campo, valor in dados.items():
        setattr(aluno, campo, valor)
    aluno.save()
    return aluno


def desativar(aluno: Aluno) -> None:
    aluno.ativo = False
    aluno.save(update_fields=['ativo'])


def reativar(aluno: Aluno) -> None:
    aluno.ativo = True
    aluno.save(update_fields=['ativo'])


@transaction.atomic
def matricular(aluno: Aluno, turma, ano_letivo) -> MatriculaTurma:
    existente = MatriculaTurma.objects.filter(aluno=aluno, ano_letivo=ano_letivo, ativo=True).first()
    if existente:
        raise ValueError('Aluno já possui matrícula ativa neste ano letivo.')
    return MatriculaTurma.objects.create(
        aluno=aluno,
        turma=turma,
        ano_letivo=ano_letivo,
        situacao=SituacaoMatricula.MATRICULADO,
    )


@transaction.atomic
def trocar_turma(matricula: MatriculaTurma, nova_turma) -> MatriculaTurma:
    matricula.turma = nova_turma
    matricula.save(update_fields=['turma'])
    return matricula


def _encerrar_matricula(matricula: MatriculaTurma, situacao: str) -> MatriculaTurma:
    matricula.situacao = situacao
    matricula.ativo    = False
    matricula.save(update_fields=['situacao', 'ativo'])
    if situacao in (SituacaoMatricula.TRANSFERIDO, SituacaoMatricula.EVADIDO):
        Aluno.objects.filter(pk=matricula.aluno_id).update(ativo=False)
    return matricula


@transaction.atomic
def transferir(matricula: MatriculaTurma) -> MatriculaTurma:
    return _encerrar_matricula(matricula, SituacaoMatricula.TRANSFERIDO)


@transaction.atomic
def evadir(matricula: MatriculaTurma) -> MatriculaTurma:
    return _encerrar_matricula(matricula, SituacaoMatricula.EVADIDO)


@transaction.atomic
def concluir(matricula: MatriculaTurma) -> MatriculaTurma:
    return _encerrar_matricula(matricula, SituacaoMatricula.CONCLUINTE)


@transaction.atomic
def ativar_acesso(aluno: Aluno, email: str, senha: str) -> Aluno:
    from apps.core.services import usuario_service, vinculo_service

    User = get_user_model()
    if User.objects.filter(email=email).exists():
        raise ValueError('Já existe um usuário cadastrado com este e-mail.')

    usuario = usuario_service.criar(email=email, nome=aluno.nome_completo, password=senha)
    aluno.usuario = usuario
    aluno.save(update_fields=['usuario'])

    vinculo = vinculo_service.criar_vinculo(usuario, aluno.escola)
    vinculo_service.adicionar_papel(vinculo, 'ALUNO')
    return aluno
