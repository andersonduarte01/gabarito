def base_template(request):
    papel = getattr(request, 'papel', None)
    if papel and papel.tipo == 'FUNCIONARIO':
        from apps.colaborador.services.permissao_service import get_modulos as _get_modulos
        modulos_permitidos = set()
        try:
            funcao = papel.perfil_colaborador.funcao
            if funcao:
                modulos_permitidos = _get_modulos(funcao)
        except Exception:
            pass
        return {
            'base_template':     'base/base_colaborador.html',
            'modulos_permitidos': modulos_permitidos,
        }
    if papel and papel.tipo == 'PROFESSOR':
        return {'base_template': 'base/base_professor.html'}
    if papel and papel.tipo == 'ALUNO':
        return {'base_template': 'base/base_aluno.html'}
    if papel and papel.tipo == 'RESPONSAVEL':
        return {'base_template': 'base/base_responsavel.html'}
    return {'base_template': 'base/base_diretor.html'}
