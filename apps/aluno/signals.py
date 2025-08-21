# alunos/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Aluno
from ..sala.models import Sala


def atualizar_total_alunos(sala):
    if sala:
        total = Aluno.objects.filter(sala=sala).count()
        sala.total_alunos = total
        sala.save(update_fields=['total_alunos'])


@receiver(post_save, sender=Aluno)
def atualizar_total_alunos_apos_salvar(sender, instance, **kwargs):
    atualizar_total_alunos(instance.sala)


@receiver(post_delete, sender=Aluno)
def atualizar_total_alunos_apos_excluir(sender, instance, **kwargs):
    atualizar_total_alunos(instance.sala)
