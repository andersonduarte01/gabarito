from django.db import transaction

from apps.core.models import TipoVinculo
from apps.core.services import vinculo_service
from apps.responsavel.models import PerfilResponsavel, VinculoResponsavelAluno


@transaction.atomic
def criar(escola, usuario_dados: dict, perfil_dados: dict) -> PerfilResponsavel:
    """Cria responsável com acesso ao sistema (com Usuario)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    email = usuario_dados['email']
    nome  = usuario_dados['nome']

    senha = usuario_dados.get('senha')
    usuario = User.objects.filter(email=email).first()
    if usuario:
        perfil, _ = PerfilResponsavel.objects.get_or_create(
            usuario=usuario,
            defaults={'nome': nome, 'escola': escola, **{k: v for k, v in perfil_dados.items() if k != 'nome'}},
        )
    else:
        usuario = User.objects.create(email=email, nome=nome, is_active=True)
        if senha:
            usuario.set_password(senha)
        else:
            usuario.set_unusable_password()
        usuario.save(update_fields=['password'])
        perfil = PerfilResponsavel.objects.create(
            usuario=usuario, nome=nome, escola=escola,
            **{k: v for k, v in perfil_dados.items() if k != 'nome'},
        )

    vinculo = vinculo_service.criar_vinculo(usuario, escola)
    vinculo_service.adicionar_papel(vinculo, TipoVinculo.RESPONSAVEL)
    return perfil


@transaction.atomic
def criar_sem_acesso(escola, perfil_dados: dict) -> PerfilResponsavel:
    """Cria responsável sem login — apenas dados de contato."""
    return PerfilResponsavel.objects.create(usuario=None, escola=escola, **perfil_dados)


def editar(perfil: PerfilResponsavel, dados: dict) -> PerfilResponsavel:
    for campo, valor in dados.items():
        setattr(perfil, campo, valor)
    perfil.save()
    return perfil


@transaction.atomic
def desativar(papel, desativado_por=None) -> None:
    from apps.core.services.vinculo_service import remover_papel
    try:
        perfil = PerfilResponsavel.objects.get(usuario=papel.vinculo.usuario)
        VinculoResponsavelAluno.objects.filter(responsavel=perfil).update(ativo=False)
    except (PerfilResponsavel.DoesNotExist, AttributeError):
        pass
    remover_papel(papel)


@transaction.atomic
def vincular_aluno(perfil: PerfilResponsavel, aluno, dados: dict) -> VinculoResponsavelAluno:
    vinculo, criado = VinculoResponsavelAluno.objects.get_or_create(
        responsavel=perfil, aluno=aluno,
        defaults={**dados, 'ativo': True},
    )
    if not criado:
        for campo, valor in dados.items():
            setattr(vinculo, campo, valor)
        vinculo.ativo = True
        vinculo.save()
    return vinculo


@transaction.atomic
def desvincular_aluno(vinculo: VinculoResponsavelAluno) -> None:
    vinculo.ativo = False
    vinculo.save(update_fields=['ativo'])
