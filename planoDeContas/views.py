from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics

from planoDeContas.models import PlanoAccount
from planoDeContas.serializers import PlanoDeContasModelSerializer, PlanoDeContasRetrieveUpdateModel

from .filters import PlanoDeContasFilter


class PlanoDeContasAPIView(generics.ListCreateAPIView):
    serializer_class = PlanoDeContasModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlanoDeContasFilter

    def get_queryset(self):
        """
        Filtra as contas dependendo da existência de uma pesquisa:
        - Se houver pesquisa (q), retorna todas as contas e aplica o filtro.
        - Caso contrário, retorna apenas contas sem vínculo.
        """
        q = self.request.query_params.get('q', None)  # Verifica se há pesquisa

        if q:
            # Se houver pesquisa, retorna todas as contas e aplica o filtro
            return PlanoAccount.objects.all()  # Aplica o filtro de pesquisa a todas as contas

        # Se não houver pesquisa, retorna apenas as contas sem vínculo
        return PlanoAccount.objects.filter(vinculo__isnull=True)

    def get_serializer_context(self):
        """Passa o contexto para o serializer incluindo controle de profundidade (depth e max_depth) controle de loop"""
        context = super().get_serializer_context()
        context['request'] = self.request
        context['depth'] = 0  # Inicia na profundidade 0
        context['max_depth'] = 10  # Máximo de 10 níveis de profundidade
        return context


class PlanoDeContasRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanoAccount.objects.all()
    serializer_class = PlanoDeContasRetrieveUpdateModel
