def _get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or ''


def registrar(request, acao, objeto, descricao):
    from apps.auditoria.models import LogAuditoria
    usuario    = request.user if request.user.is_authenticated else None
    papel      = getattr(request, 'papel', None)
    escola     = getattr(request, 'escola', None)
    papel_tipo = papel.tipo if papel else ''
    LogAuditoria.objects.create(
        usuario    = usuario,
        escola     = escola,
        papel_tipo = papel_tipo,
        acao       = acao,
        modelo     = objeto.__class__.__name__,
        objeto_id  = str(objeto.pk),
        descricao  = descricao,
        ip         = _get_ip(request),
    )


def listar_escola(escola, filtros=None):
    from apps.auditoria.models import LogAuditoria
    qs = LogAuditoria.objects.filter(escola=escola).select_related('usuario')
    if filtros:
        if filtros.get('acao'):
            qs = qs.filter(acao=filtros['acao'])
        if filtros.get('modelo'):
            qs = qs.filter(modelo__icontains=filtros['modelo'])
    return qs


def listar_plataforma(filtros=None):
    from apps.auditoria.models import LogAuditoria
    qs = LogAuditoria.objects.all().select_related('usuario', 'escola')
    if filtros:
        if filtros.get('acao'):
            qs = qs.filter(acao=filtros['acao'])
        if filtros.get('escola'):
            qs = qs.filter(escola=filtros['escola'])
    return qs
