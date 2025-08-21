from django.apps import AppConfig


class AlunoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.aluno'

    def ready(self):
        import apps.aluno.signals