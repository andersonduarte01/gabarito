from django.db import transaction
from django.shortcuts import get_object_or_404, get_list_or_404

from .models import *
from ..aluno.models import Aluno


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


def correcao(gabarito):
    respostas = Resposta.objects.filter(gabarito=gabarito)
    gabarito.qtd_acertos = 0
    for r in respostas:
        q = Questao.objects.get(pk=r.questao.id)
        if(r.resposta == q.opcao_certa):
            r.acertou = True
            gabarito.qtd_acertos += 1
            gabarito.save()
            r.save()
        else:
            r.acertou = False
            r.save()

    return respostas



def alunos_prova(avaliacao, alunos):
    questoes = len(Questao.objects.filter(avaliacao=avaliacao))
    alunos_gabarito = []
    aluno_aval_falta = []
    for aluno in alunos:
        try:
            aluno_prova_ok = get_object_or_404(Gabarito, avaliacao=avaliacao, aluno=aluno)
            correcao(aluno_prova_ok)
            alunos_gabarito.append(aluno_prova_ok)
        except:
            aluno_aval_falta.append(aluno)

    return alunos_gabarito, aluno_aval_falta, questoes


def acertos_por_questao(avaliacao):
    resultados = []
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao)
    questoes = get_list_or_404(Questao, avaliacao=avaliacao)

    for questao in questoes:
        acertos = 0
        acerts = 0
        conjunto = []
        respostas = Resposta.objects.filter(questao=questao, acertou=True)
        respostasALL = Resposta.objects.filter(questao=questao)
        try:
            acertos = float("{:.1f}".format((len(respostas)/len(respostasALL) * 100)))
            acerts = f'{len(respostas)}/{len(respostasALL)}'
        except:
            print()
        conjunto.append(questao)
        conjunto.append(acertos)
        conjunto.append(acerts)
        resultados.append(conjunto)

    return resultados

