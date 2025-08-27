from rest_framework import serializers

from app.utils.validate_document import validate_cpf_cnpj
from fornecedores.models import Fornecedores


class FornecedorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedores
        fields = '__all__'

    def validate_documento(self, value):
        # Validação de CPF/CNPJ
        validate_cpf_cnpj(value)
        return value
