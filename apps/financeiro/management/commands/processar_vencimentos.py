from django.core.management.base import BaseCommand

from apps.financeiro.services import financeiro_service


class Command(BaseCommand):
    help = 'Verifica cobranças vencidas e transiciona PENDENTE → VENCIDO'

    def handle(self, *args, **options):
        total = financeiro_service.verificar_vencimentos()
        self.stdout.write(self.style.SUCCESS(f'{total} cobranças marcadas como VENCIDO'))
