import datetime

from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import ExtractMonth
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import SalaForm, EditarSalaForm
from .permissoes import IsUnidadeEscolar
from .serializers import SalaSerializer, SalaUpdateSerializer, AnoSerializer, AlunoSerializer, ProfessorSalasSerializer
from ..aluno.models import Aluno
from ..avaliacao.models import Avaliacao
from ..escola.models import UnidadeEscolar, AnoLetivo
from ..frequencia.models import Registro
from ..funcionario.models import Professor
from ..sala.models import Sala, Ano


class AdicionarSala(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = SalaForm
    model = Sala
    template_name = 'sala/adicionar_sala.html'
    success_message = 'Sala cadastrada com sucesso.'
    success_url = reverse_lazy('escola:dash_escola')

    def get_escola(self):
        return get_object_or_404(UnidadeEscolar, pk=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        escola = self.get_escola()
        context['escola'] = escola
        return context

    def form_valid(self, form):
        sala = form.save(commit=False)
        sala.escola = self.get_escola()
        sala.save()
        return super().form_valid(form)


class EditarSala(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = EditarSalaForm
    model = Sala
    success_message = 'Sala atualizada com sucesso.'
    template_name = 'sala/editar_sala.html'

    def get_success_url(self):
        return reverse('escola:dash_escola')


class DeletarSala(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sala
    success_message = 'Sala removida com sucesso!'

    def get_object(self, queryset=None):
        return Sala.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('escola:dash_escola')


##### API ####
class SalaViewSet(viewsets.ModelViewSet):
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticated]
    queryset = Sala.objects.all()

    def perform_create(self, serializer):
        usuario = self.request.user

        # pega a escola vinculada ao usuário logado
        try:
            escola = UnidadeEscolar.objects.get(pk=usuario.pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Usuário logado não é uma escola válida.")

        # pega o ano letivo corrente
        ano_corrente = AnoLetivo.objects.filter(corrente=True).first()
        if not ano_corrente:
            raise serializers.ValidationError("Não existe ano letivo corrente configurado.")

        serializer.save(escola=escola, ano_letivo=ano_corrente)

    @action(detail=False, methods=['get'], url_path='ano-corrente')
    def ano_corrente(self, request):
        ano_corrente = AnoLetivo.objects.filter(corrente=True).first()
        if not ano_corrente:
            return Response([])

        queryset = Sala.objects.filter(ano_letivo=ano_corrente, escola=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EditarExcluirSala(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sala.objects.all()
    serializer_class = SalaUpdateSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        sala = self.get_object()
        sala.delete()
        return Response({"detail": "Sala deletada com sucesso."}, status=status.HTTP_204_NO_CONTENT)


class NoPagination(PageNumberPagination):
    page_size = None


class AnoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ano.objects.all().order_by('descricao')
    serializer_class = AnoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NoPagination


class AlunoViewSet(viewsets.ModelViewSet):
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sala_id = self.kwargs.get('sala_pk')
        return Aluno.objects.filter(sala_id=sala_id).order_by(
            'nome', )

    def perform_create(self, serializer):
        sala_id = self.kwargs.get('sala_pk')
        try:
            sala = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            raise ValidationError("Sala não encontrada.")
        serializer.save(sala=sala)

    def perform_update(self, serializer):
        # Permite atualizar apenas os campos nome, data_nascimento e sexo
        serializer.save()


class ProfessorSalasViewSet(viewsets.ModelViewSet):
    serializer_class = ProfessorSalasSerializer
    permission_classes = [IsAuthenticated]
    queryset = Sala.objects.all()


    @action(detail=False, methods=['get'], url_path='ano-corrente')
    def ano_corrente(self, request):
        ano_corrente = AnoLetivo.objects.filter(corrente=True).first()
        if not ano_corrente:
            return Response([])

        professor = Professor.objects.get(pk=request.user.pk)
        escola = UnidadeEscolar.objects.get(pk=professor.escola.pk)
        queryset = Sala.objects.filter(ano_letivo=ano_corrente, escola=escola)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)