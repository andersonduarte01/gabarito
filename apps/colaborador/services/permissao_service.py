from ..models import FuncaoEscolar, PermissaoFuncao


def set_permissoes(funcao: FuncaoEscolar, modulos: list) -> None:
    PermissaoFuncao.objects.filter(funcao=funcao).delete()
    PermissaoFuncao.objects.bulk_create([
        PermissaoFuncao(funcao=funcao, modulo=m) for m in modulos
    ])


def get_modulos(funcao: FuncaoEscolar) -> set:
    return set(PermissaoFuncao.objects.filter(funcao=funcao).values_list('modulo', flat=True))


def tem_permissao(papel, modulo: str) -> bool:
    if papel.tipo != 'FUNCIONARIO':
        return True
    try:
        funcao = papel.perfil_colaborador.funcao
    except Exception:
        return False
    if funcao is None:
        return False
    return PermissaoFuncao.objects.filter(funcao=funcao, modulo=modulo).exists()
