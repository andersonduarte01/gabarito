def base_template(request):
    papel = getattr(request, 'papel', None)
    if papel and papel.tipo == 'FUNCIONARIO':
        return {'base_template': 'base/base_colaborador.html'}
    if papel and papel.tipo == 'PROFESSOR':
        return {'base_template': 'base/base_professor.html'}
    return {'base_template': 'base/base_diretor.html'}
