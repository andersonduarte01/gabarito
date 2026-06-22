import datetime
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.sala.models import Turma
from apps.core.services import AlunoService


TURMAS = {
    1: {
        'ano_nasc': 2019,
        'alunos': [
            ('Ana',      'Silva',      'F'),
            ('Bruno',    'Santos',     'M'),
            ('Carla',    'Oliveira',   'F'),
            ('Diego',    'Costa',      'M'),
            ('Eduarda',  'Pereira',    'F'),
            ('Felipe',   'Souza',      'M'),
            ('Gabriela', 'Lima',       'F'),
            ('Henrique', 'Ferreira',   'M'),
            ('Isabela',  'Rodrigues',  'F'),
            ('Joao',     'Alves',      'M'),
        ],
    },
    2: {
        'ano_nasc': 2018,
        'alunos': [
            ('Lucas',     'Martins',   'M'),
            ('Mariana',   'Barbosa',   'F'),
            ('Nicolas',   'Gomes',     'M'),
            ('Olivia',    'Araujo',    'F'),
            ('Pedro',     'Nascimento','M'),
            ('Quezia',    'Cardoso',   'F'),
            ('Rafael',    'Melo',      'M'),
            ('Sofia',     'Teixeira',  'F'),
            ('Thiago',    'Carvalho',  'M'),
            ('Valentina', 'Ribeiro',   'F'),
        ],
    },
    3: {
        'ano_nasc': 2017,
        'alunos': [
            ('Arthur',   'Cunha',      'M'),
            ('Beatriz',  'Campos',     'F'),
            ('Carlos',   'Monteiro',   'M'),
            ('Daniela',  'Nunes',      'F'),
            ('Emanuel',  'Freitas',    'M'),
            ('Fernanda', 'Pinto',      'F'),
            ('Gustavo',  'Moreira',    'M'),
            ('Helena',   'Vieira',     'F'),
            ('Igor',     'Lopes',      'M'),
            ('Julia',    'Mendes',     'F'),
        ],
    },
}

SENHA = 'sosa1808'


class Command(BaseCommand):
    help = 'Cria 10 alunos nas turmas de id 1, 2 e 3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove os alunos do seed antes de recriar',
        )

    def handle(self, *args, **options):
        if options['reset']:
            todos_emails = [
                f'{primeiro.lower()}@gmail.com'
                for dados in TURMAS.values()
                for primeiro, _, _ in dados['alunos']
            ]
            from apps.aluno.models import Aluno
            from apps.core.models import Usuario
            pks = list(
                Aluno.objects
                .filter(usuario__email__in=todos_emails)
                .values_list('usuario_id', flat=True)
            )
            Aluno.objects.filter(usuario__email__in=todos_emails).delete()
            Usuario.objects.filter(pk__in=pks).delete()
            self.stdout.write(self.style.WARNING('Alunos anteriores removidos.'))
        criados = 0
        erros   = 0

        for turma_id, dados in TURMAS.items():
            try:
                turma = Turma.objects.select_related('escola').get(pk=turma_id)
            except Turma.DoesNotExist:
                self.stderr.write(f'Turma id={turma_id} não encontrada — pulando.')
                continue

            escola   = turma.escola
            service  = AlunoService(escola)
            ano_nasc = dados['ano_nasc']

            for i, (primeiro, sobrenome, sexo) in enumerate(dados['alunos']):
                nome      = f'{primeiro} {sobrenome}'
                email     = f'{primeiro.lower()}@gmail.com'
                data_nasc = datetime.date(ano_nasc, (i % 12) + 1, (i % 28) + 1)

                with transaction.atomic():
                    result = service.criar_aluno(
                        nome=nome,
                        email=email,
                        password=SENHA,
                        data_nascimento=data_nasc,
                        sexo=sexo,
                        sala=turma,
                        tem_responsavel=False,
                        telefone=f'(83) 9{turma_id}{i:04d}-{(i * 3 + 1):04d}',
                        responsavel_legal='',
                        telefone_responsavel='',
                    )

                if result['status'] in ('created', 'ok'):
                    mat = result['aluno'].matricula
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[Turma {turma_id}] {nome} — {email} — matrícula {mat}'
                        )
                    )
                    criados += 1
                elif result['status'] == 'exists':
                    self.stdout.write(f'[Turma {turma_id}] {nome} já existe ({email})')
                else:
                    self.stderr.write(
                        self.style.ERROR(f'[Turma {turma_id}] {nome}: {result["message"]}')
                    )
                    erros += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{criados} aluno(s) criado(s), {erros} erro(s).'))
