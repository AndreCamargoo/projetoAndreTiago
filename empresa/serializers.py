from rest_framework import serializers

from app.utils.validate_document import validate_cpf_cnpj

from .models import Empresa, Socio, Atividade
from accounts.serializers import UserModelSerializer


class SocioModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__'


class AtividadeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'


class EmpresaSerializerModelSerializer(serializers.ModelSerializer):
    # Nested serializer
    user = UserModelSerializer(read_only=True)
    socios = SocioModelSerializer(many=True, read_only=True)
    atividades = AtividadeModelSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True, 'default': serializers.CurrentUserDefault()},
            'nome': {'required': False},
            'status': {'required': False},
            'logradouro': {'required': False},
            'numero': {'required': False},
            'bairro': {'required': False},
            'cidade': {'required': False},
            'estado': {'required': False},
            'cep': {'required': False},
            'pais': {'required': False},
            'nome_fantasia': {'required': False},
            'data_abertura': {'required': False},
            'capital_social': {'required': False},
            'atividade_principal': {'required': False},
            'atividades_secundarias': {'required': False},
            'porte': {'required': False},
            'complemento': {'required': False},
            'telefone': {'required': False},
            'email': {'required': False},
        }

    def create(self, validated_data):
        # Garante que o user seja definido automaticamente
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_documento(self, value):
        # Validação de CPF/CNPJ
        validate_cpf_cnpj(value)
        return value

    def validate(self, data):
        tipo_documento = data.get("tipo_documento")

        campos_pj_obrigatorios = [
            'data_abertura',
            'status',
            'capital_social',
            'atividade_principal',
            'porte'
        ]

        # Se for PJ, não precisa de outros dados obrigatórios
        if tipo_documento == 'PJ':
            # Aqui você só valida os campos que podem ser preenchidos no corpo da requisição
            # Os campos obrigatórios da PJ (nome, logradouro, etc) serão preenchidos pela API
            for campo in campos_pj_obrigatorios:
                if campo in data and not data.get(campo):
                    raise serializers.ValidationError(
                        {campo: f"Campo obrigatório para Pessoa Jurídica."})

        # Se for PF, exige todos os campos obrigatórios
        if tipo_documento == 'PF':
            campos_pf_obrigatorios = [
                'nome', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'pais'
            ]
            for campo in campos_pf_obrigatorios:
                if campo not in data or not data.get(campo):
                    raise serializers.ValidationError(
                        {campo: f"Campo obrigatório para Pessoa Física."})

        return data


class EmpresaUpdateModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer(read_only=True)
    socios = SocioModelSerializer(many=True, read_only=True)
    atividades = AtividadeModelSerializer(many=True, read_only=True)

    # Campo customizado para receber array de atividades secundárias
    atividades_secundarias_array = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Empresa
        fields = '__all__'

        # Todos os campos são opcionais no update
        # user, tipo_documento, documento, capital_social não pode ser alterado
        extra_kwargs = {
            'user': {'required': False, 'read_only': True},
            'tipo_documento': {'required': False, 'read_only': True},
            'documento': {'required': False, 'read_only': True},
            'capital_social': {'required': False, 'read_only': True},
            'nome': {'required': False},
            'status': {'required': False},
            'logradouro': {'required': False},
            'numero': {'required': False},
            'bairro': {'required': False},
            'cidade': {'required': False},
            'estado': {'required': False},
            'cep': {'required': False},
            'pais': {'required': False},
            'atividade_principal': {'required': False},
            'atividades_secundarias': {'read_only': True},
            'complemento': {'required': False},
            'telefone': {'required': False},
            'email': {'required': False},
        }

    def validate_documento(self, value):
        # No update, não permite alterar o documento
        if self.instance and self.instance.documento != value:
            raise serializers.ValidationError(
                "Não é permitido alterar o CNPJ/CPF")
        return value

    def validate(self, data):
        # Converte array para string se necessário
        if 'atividades_secundarias_array' in data:
            data['atividades_secundarias'] = ", ".join(
                data.pop('atividades_secundarias_array'))

        # Valida campos obrigatórios que estão null no banco
        instance = self.instance
        if instance:
            if instance.tipo_documento == 'PF':
                campos_obrigatorios = [
                    'nome', 'logradouro', 'numero', 'bairro',
                    'cidade', 'estado', 'cep', 'pais'
                ]
            else:  # PJ
                campos_obrigatorios = [
                    'nome', 'status', 'logradouro', 'numero', 'bairro',
                    'cidade', 'estado', 'cep', 'pais', 'atividade_principal'
                ]

            erros = {}
            for campo in campos_obrigatorios:
                # Se o campo está null no banco E não foi enviado no update
                valor_atual = getattr(instance, campo)
                if (valor_atual in [None, ''] or
                        (isinstance(valor_atual, str) and valor_atual.strip() == '')) and campo not in data:
                    erros[campo] = f"Campo obrigatório. Está vazio no banco de dados."

            if erros:
                raise serializers.ValidationError(erros)

        return data


class SocioModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__'
        extra_kwargs = {
            'empresa': {'read_only': True}  # Agora não precisa enviar no POST
        }


class AtividadeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'
        extra_kwargs = {
            'empresa': {'read_only': True}  # Agora não precisa enviar no POST
        }
