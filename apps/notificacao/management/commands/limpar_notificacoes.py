from django.core.management.base import BaseCommand

from apps.notificacao.services import notificacao_service


class Command(BaseCommand):
    help = 'Remove notificações lidas há mais de 60 dias.'

    def handle(self, *args, **options):
        deletadas = notificacao_service.limpar_antigas()
        self.stdout.write(self.style.SUCCESS(f'{deletadas} notificação(ões) removida(s).'))
