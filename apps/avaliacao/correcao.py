from django.db import transaction

from .models import *

@transaction.atomic
def criarGabaritos(avaliacao, sala):
    alunos = Aluno.objects.filter(sala=sala)
    gabaritos = []
    for aluno in alunos:
        try:
            gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
        except:
            gabaritos.append(
                Gabarito(avaliacao=avaliacao, aluno=aluno)
            )

    Gabarito.objects.bulk_create(gabaritos)


@transaction.atomic
def correcao(gabarito):
    respostas = Resposta.objects.filter(gabarito=gabarito)

    for r in respostas:
        q = Questao.objects.get(pk=r.questao.id)
        gabarito.qtd_acertos = 0
        if(r.resposta == q.opcao_certa):
            r.acertou = True
            gabarito.qtd_acertos += 1
            gabarito.save()
            r.save()
        else:
            r.acertou = False
            r.save()


@transaction.atomic
def alinharquestoes(avaliacao, sala):
    alunos = Aluno.objects.filter(sala=sala)
    questoes = Questao.objects.filter(avaliacao=avaliacao).order_by('numero')
    for aluno in alunos:
            gabarito = Gabarito.objects.get(aluno=aluno, avaliacao=avaliacao)
            gabarito_atualizar = []
            for q in questoes:
                try:
                    r = Resposta.objects.get(questao=q, gabarito=gabarito)
                except:
                    gabarito_atualizar.append(
                        Resposta(gabarito=gabarito, questao=q)
                    )
            Resposta.objects.bulk_create(gabarito_atualizar)
            correcao(gabarito=gabarito)


