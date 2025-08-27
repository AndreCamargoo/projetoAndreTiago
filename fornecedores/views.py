from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics

from fornecedores.models import Fornecedores
from fornecedores.serializers import FornecedorModelSerializer
from .filters import FornecedorFilter


class FornecedorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Fornecedores.objects.all()
    serializer_class = FornecedorModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FornecedorFilter


class FornecedorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fornecedores.objects.all()
    serializer_class = FornecedorModelSerializer
