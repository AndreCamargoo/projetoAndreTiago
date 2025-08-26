import requests
from django.db import transaction
from django.conf import settings

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Empresa, Socio, Atividade
from .utils.atividade_utils import AtividadeUtils
from .utils.companySave import CompanySave
from .serializers import EmpresaSerializerModelSerializer, EmpresaUpdateModelSerializer, AtividadeModelSerializer, SocioModelSerializer
from app.utils.exceptions import ValidationError


class EmpresaAPIView(APIView):
    def get(self, request):
        empresas = Empresa.objects.filter(user_id=request.user.id)
        serializer = EmpresaSerializerModelSerializer(empresas, many=True)
        return Response(serializer.data)

    def post(self, request):
        documento = request.data.get('documento')
        tipo_documento = request.data.get('tipo_documento')

        # Validação básica dos campos obrigatórios
        if not documento:
            raise ValidationError("Documento é obrigatório.")

        if not tipo_documento:
            raise ValidationError("Tipo de documento é obrigatório")

        # Quando for PJ, busca dados da API
        if tipo_documento == 'PJ':
            url = f'https://api.cnpja.com/office/{documento}'
            headers = {
                "Authorization": settings.CNPJA_API_TOKEN,
                "Accept": "application/json"
            }

            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return Response(
                        {"erro": "Erro ao buscar dados na API externa."},
                        status=response.status_code
                    )

                data_cnpja = response.json()

                # Preenche os dados com a API
                empresa = CompanySave(
                    data_cnpja, request.data, request.user).processar()

                return Response(
                    EmpresaSerializerModelSerializer(empresa).data,
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"erro": f"Erro ao processar dados da API: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Quando for PF, valida e cria normalmente
        elif tipo_documento == 'PF':
            serializer = EmpresaSerializerModelSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"erro": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"erro": "Tipo de documento inválido."},
            status=status.HTTP_400_BAD_REQUEST
        )


class EmpresaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Empresa.objects.all()
    lookup_field = 'documento'  # Para usar CNPJ/CPF em vez de ID

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmpresaUpdateModelSerializer
        return EmpresaSerializerModelSerializer


class AtividadeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AtividadeModelSerializer

    def get_queryset(self):
        documento = self.kwargs['documento']
        return Atividade.objects.filter(
            empresa__documento=documento,
            empresa__user=self.request.user
        ).order_by('-id')

    @transaction.atomic
    def perform_create(self, serializer):
        documento = self.kwargs['documento']
        try:
            empresa = Empresa.objects.get(
                documento=documento,
                user=self.request.user
            )

            atividade = serializer.save(empresa=empresa)

            if atividade.principal:
                AtividadeUtils.atualizar_atividade_principal(
                    empresa, atividade)
            else:
                AtividadeUtils.atualizar_atividades_secundarias(empresa)

        except Empresa.DoesNotExist:
            raise ValidationError("Empresa não encontrada")


class AtividadeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AtividadeModelSerializer

    def get_queryset(self):
        documento = self.kwargs['documento']
        return Atividade.objects.filter(
            empresa__documento=documento,
            empresa__user=self.request.user
        )

    @transaction.atomic
    def perform_update(self, serializer):
        atividade = self.get_object()
        old_principal = atividade.principal
        empresa = atividade.empresa

        updated_atividade = serializer.save()

        if updated_atividade.principal or (old_principal and updated_atividade.principal):
            AtividadeUtils.atualizar_atividade_principal(
                empresa, updated_atividade)
        else:
            AtividadeUtils.atualizar_atividades_secundarias(empresa)

        if old_principal and not updated_atividade.principal:
            nova_principal = Atividade.objects.filter(
                empresa=empresa,
                principal=True
            ).first()

            if nova_principal:
                empresa.atividade_principal = nova_principal.descricao
            else:
                empresa.atividade_principal = None

            empresa.save()
            AtividadeUtils.atualizar_atividades_secundarias(empresa)

    @transaction.atomic
    def perform_destroy(self, instance):
        empresa = instance.empresa
        was_principal = instance.principal

        instance.delete()

        if was_principal:
            nova_principal = Atividade.objects.filter(
                empresa=empresa,
                principal=True
            ).first()

            if nova_principal:
                empresa.atividade_principal = nova_principal.descricao
            else:
                empresa.atividade_principal = None

            AtividadeUtils.atualizar_atividades_secundarias(empresa)
            empresa.save()
        else:
            AtividadeUtils.atualizar_atividades_secundarias(empresa)


class SocioListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SocioModelSerializer

    def get_queryset(self):
        documento = self.kwargs['documento']
        return Socio.objects.filter(
            empresa__documento=documento,
            empresa__user=self.request.user
        ).order_by('-id')

    @transaction.atomic
    def perform_create(self, serializer):
        documento = self.kwargs['documento']
        try:
            # Busca a Empresa pelo documento
            empresa = Empresa.objects.get(
                documento=documento,
                user=self.request.user
            )

            # Salva o sócio vinculado à empresa
            serializer.save(empresa=empresa)

        except Empresa.DoesNotExist:
            raise ValidationError("Empresa não encontrada")


class SocioRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Socio.objects.all()
    serializer_class = SocioModelSerializer
