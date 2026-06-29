from django.db import transaction

from apps.core.models import TipoVinculo
from apps.core.services import vinculo_service
from apps.professor.models import FormacaoAcademica, PerfilProfessor


@transaction.atomic
def criar(escola, usuario_dados: dict, perfil_dados: dict, criado_por) -> PerfilProfessor:
    """Cria/reutiliza Usuario + VinculoEscola + PapelVinculo(PROFESSOR) + PerfilProfessor."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    usuario, _ = User.objects.get_or_create(
        email=usuario_dados['email'],
        defaults={'nome': usuario_dados['nome'], 'is_active': True},
    )

    vinculo = vinculo_service.criar_vinculo(usuario, escola)
    papel   = vinculo_service.adicionar_papel(vinculo, TipoVinculo.PROFESSOR)

    perfil = PerfilProfessor.objects.create(
        papel=papel,
        cpf=perfil_dados.get('cpf', ''),
        rg=perfil_dados.get('rg', ''),
        data_nascimento=perfil_dados.get('data_nascimento'),
        telefone=perfil_dados.get('telefone', ''),
        data_admissao=perfil_dados.get('data_admissao'),
        tipo_vinculo=perfil_dados.get('tipo_vinculo', 'CLT'),
        registro_profissional=perfil_dados.get('registro_profissional', ''),
    )
    return perfil


def editar(perfil: PerfilProfessor, dados: dict) -> PerfilProfessor:
    for campo, valor in dados.items():
        setattr(perfil, campo, valor)
    perfil.save()
    return perfil


@transaction.atomic
def desativar(papel, desativado_por) -> None:
    from apps.core.services.vinculo_service import remover_papel
    remover_papel(papel)


@transaction.atomic
def reativar(papel) -> None:
    papel.ativo = True
    papel.save(update_fields=['ativo'])


@transaction.atomic
def salvar_endereco(perfil: PerfilProfessor, dados: dict) -> PerfilProfessor:
    from apps.core.models import Endereco
    if perfil.endereco_id:
        for campo, valor in dados.items():
            setattr(perfil.endereco, campo, valor)
        perfil.endereco.save()
    else:
        endereco = Endereco.objects.create(**dados)
        perfil.endereco = endereco
        perfil.save(update_fields=['endereco'])
    return perfil


@transaction.atomic
def adicionar_formacao(perfil: PerfilProfessor, dados: dict) -> FormacaoAcademica:
    return FormacaoAcademica.objects.create(professor=perfil, **dados)


@transaction.atomic
def remover_formacao(formacao: FormacaoAcademica) -> None:
    formacao.delete()


@transaction.atomic
def vincular_turma(perfil: PerfilProfessor, turma, ano_letivo):
    from apps.turma.models import ProfessorTurma
    obj, _ = ProfessorTurma.objects.update_or_create(
        turma=turma, ano_letivo=ano_letivo,
        defaults={'professor': perfil, 'ativo': True},
    )
    return obj


@transaction.atomic
def vincular_materia_turma(perfil: PerfilProfessor, materia, turma, ano_letivo):
    from apps.turma.models import ProfessorMateriaTurma
    obj, _ = ProfessorMateriaTurma.objects.update_or_create(
        materia=materia, turma=turma, ano_letivo=ano_letivo,
        defaults={'professor': perfil, 'ativo': True},
    )
    return obj


def calcular_carga_horaria(perfil: PerfilProfessor, ano_letivo) -> float:
    """Retorna carga horária semanal em horas, derivada dos HorarioAula ativos."""
    from apps.turma.models import HorarioAula
    from datetime import datetime
    horarios = HorarioAula.objects.filter(
        professor=perfil, ano_letivo=ano_letivo, ativo=True,
    ).select_related('periodo')
    total_minutos = 0
    for h in horarios:
        inicio = datetime.combine(datetime.today(), h.periodo.hora_inicio)
        fim    = datetime.combine(datetime.today(), h.periodo.hora_fim)
        total_minutos += (fim - inicio).seconds // 60
    return round(total_minutos / 60, 1)
