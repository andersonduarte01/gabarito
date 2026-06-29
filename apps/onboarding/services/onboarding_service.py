from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.core.models import PapelVinculo, TipoVinculo
from apps.core.services import vinculo_service
from apps.diretor.models import CargoDiretor, PerfilDiretor
from apps.escola.models import UnidadeEscolar
from apps.escola.services import escola_service
from apps.onboarding.models import CanalConvite, ConviteOnboarding

User = get_user_model()


@transaction.atomic
def criar_escola_e_convite(
    dados_escola: dict,
    dados_diretor: dict,
    canal_envio: str,
    criado_por,
) -> tuple[UnidadeEscolar, ConviteOnboarding]:
    escola = escola_service.criar(dados_escola, criado_por)

    email    = dados_diretor['email']
    nome     = dados_diretor['nome']
    telefone = dados_diretor.get('telefone', '')

    usuario, criado = User.objects.get_or_create(
        email=email,
        defaults={'nome': nome, 'is_active': True},
    )
    if criado:
        usuario.set_unusable_password()
        usuario.save(update_fields=['password'])

    vinculo = vinculo_service.criar_vinculo(usuario, escola)
    vinculo_service.adicionar_papel(vinculo, TipoVinculo.DIRETOR)

    convite = ConviteOnboarding.objects.create(
        escola=escola,
        email=email,
        telefone=telefone,
        canal_envio=canal_envio,
    )

    _enviar_convite(convite)
    return escola, convite


@transaction.atomic
def reenviar_convite(escola: UnidadeEscolar, canal_envio: str, criado_por) -> ConviteOnboarding:
    ultimo = escola.convites.order_by('-criado_em').first()
    if not ultimo:
        raise ValueError('Nenhum convite encontrado para esta escola.')

    email    = ultimo.email
    telefone = ultimo.telefone

    escola.convites.filter(usado=False).update(usado=True)

    convite = ConviteOnboarding.objects.create(
        escola=escola,
        email=email,
        telefone=telefone,
        canal_envio=canal_envio,
    )
    _enviar_convite(convite)
    return convite


def validar_token(token: str) -> ConviteOnboarding:
    try:
        convite = ConviteOnboarding.objects.select_related('escola').get(token=token)
    except ConviteOnboarding.DoesNotExist:
        raise ValueError('Link inválido.')
    if not convite.valido:
        raise ValueError('Link expirado ou já utilizado.')
    return convite


@transaction.atomic
def completar_onboarding(token: str, senha: str, dados_perfil: dict) -> tuple:
    convite = validar_token(token)

    usuario = User.objects.get(email=convite.email)
    usuario.set_password(senha)
    usuario.save(update_fields=['password'])

    papel = (
        PapelVinculo.objects
        .filter(
            vinculo__usuario=usuario,
            vinculo__escola=convite.escola,
            tipo=TipoVinculo.DIRETOR,
            ativo=True,
        )
        .first()
    )
    if not papel:
        raise ValueError('Vínculo de Diretor não encontrado para este convite.')

    if hasattr(papel, 'perfil_diretor'):
        raise ValueError('Cadastro já concluído para este convite.')

    perfil = PerfilDiretor.objects.create(
        papel=papel,
        cargo=dados_perfil.get('cargo', CargoDiretor.TITULAR),
        cpf=dados_perfil.get('cpf', ''),
        data_nascimento=dados_perfil.get('data_nascimento'),
        telefone=dados_perfil.get('telefone', ''),
        data_inicio=dados_perfil.get('data_inicio'),
    )

    convite.usado = True
    convite.save(update_fields=['usado'])

    return usuario, perfil


# ---------------------------------------------------------------------------
# Envio de convite (privado)
# ---------------------------------------------------------------------------

def _enviar_convite(convite: ConviteOnboarding) -> None:
    from django.conf import settings
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    link     = f'{base_url}/onboarding/convite/{convite.token}/'

    if convite.canal_envio == CanalConvite.EMAIL:
        send_mail(
            subject=f'Convite EduCare — {convite.escola.nome}',
            message=(
                f'Olá!\n\n'
                f'Você foi cadastrado como Diretor da escola "{convite.escola.nome}" '
                f'no EduCare.\n\n'
                f'Acesse o link abaixo para definir sua senha e completar seu cadastro:\n'
                f'{link}\n\n'
                f'Este link é válido por 72 horas.\n\n'
                f'Equipe EduCare'
            ),
            from_email='noreply@educare.com.br',
            recipient_list=[convite.email],
            fail_silently=True,
        )
