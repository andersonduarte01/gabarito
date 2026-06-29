def notificacoes_counter(request):
    if not request.user.is_authenticated:
        return {'notificacoes_nao_lidas': 0}
    from apps.notificacao.services.notificacao_service import listar_nao_lidas
    return {'notificacoes_nao_lidas': listar_nao_lidas(request.user).count()}
