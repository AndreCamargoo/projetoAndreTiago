from collections import OrderedDict
from rest_framework import serializers
from planoDeContas.models import PlanoAccount


class PlanoAccountRecursivoSerializer(serializers.ModelSerializer):
    """
    Serializer recursivo simplificado com ordem de campos controlada
    """
    subcontas = serializers.SerializerMethodField()

    class Meta:
        model = PlanoAccount
        fields = ['id', 'nome', 'codigo', 'tipo', 'descricao', 'subcontas']

    def to_representation(self, instance):
        """
        Garante que os campos mantenham a ordem definida
        """
        representation = super().to_representation(instance)

        # ORDEM ESPECÍFICA DOS CAMPOS
        ordered_representation = OrderedDict()
        ordered_representation['id'] = representation.get('id')
        ordered_representation['nome'] = representation.get('nome')
        ordered_representation['codigo'] = representation.get('codigo')
        ordered_representation['tipo'] = representation.get('tipo')
        ordered_representation['descricao'] = representation.get('descricao')
        ordered_representation['subcontas'] = representation.get('subcontas')

        return ordered_representation

    def get_subcontas(self, obj):
        """
        Método recursivo para construir a hierarquia de subcontas
        """
        depth = self.context.get('depth', 0)
        max_depth = self.context.get('max_depth', 5)

        # Condição de parada para evitar recursão infinita
        if depth >= max_depth:
            return []

        subcontas = obj.subcontas.all()

        # Incrementa a profundidade para o próximo nível
        new_context = self.context.copy()
        new_context['depth'] = depth + 1

        # Mantém a ordem também nas subcontas
        return PlanoAccountRecursivoSerializer(
            subcontas,
            many=True,
            context=new_context
        ).data


class PlanoDeContasModelSerializer(serializers.ModelSerializer):
    """
    Serializer principal para Plano de Contas com ordem controlada
    """
    tipo = serializers.ChoiceField(
        choices=[('A', 'Analítica'), ('S', 'Sintética')],
        error_messages={
            'invalid_choice': "O campo 'tipo' aceita somente os valores: 'A' (Analítica) ou 'S' (Sintética). Valor recebido: '{input}'"
        }
    )

    # Para escrita: permite vincular a uma conta pai pelo ID
    vinculo_id = serializers.PrimaryKeyRelatedField(
        queryset=PlanoAccount.objects.all(),
        source='vinculo',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Para leitura: mostra a hierarquia de subcontas simplificada
    subcontas = serializers.SerializerMethodField()

    class Meta:
        model = PlanoAccount
        fields = '__all__'

    def to_representation(self, instance):
        """
        Remove campos write-only e controla a ordem dos campos
        """
        representation = super().to_representation(instance)
        representation.pop('vinculo_id', None)  # Remove campo write-only

        # ORDEM ESPECÍFICA DOS CAMPOS (FÁCIL DE ENTENDER E MANTER)
        ordered_representation = OrderedDict()

        # Campos principais primeiro
        ordered_representation['id'] = representation.get('id')
        ordered_representation['nome'] = representation.get('nome')
        ordered_representation['codigo'] = representation.get('codigo')
        ordered_representation['tipo'] = representation.get('tipo')
        ordered_representation['descricao'] = representation.get('descricao')

        # Demais campos após
        ordered_representation['vinculo'] = representation.get('vinculo')
        ordered_representation['empresa'] = representation.get('empresa')
        ordered_representation['cadastrado_em'] = representation.get(
            'cadastrado_em')
        ordered_representation['atualizado_em'] = representation.get(
            'atualizado_em')
        ordered_representation['subcontas'] = representation.get('subcontas')

        return ordered_representation

    def get_subcontas(self, obj):
        """
        Retorna a hierarquia de subcontas usando serializer recursivo
        """
        depth = self.context.get('depth', 0)
        max_depth = self.context.get('max_depth', 5)

        # Condição de parada
        if depth >= max_depth:
            return []

        subcontas = obj.subcontas.all()

        # Incrementa a profundidade
        new_context = self.context.copy()
        new_context['depth'] = depth + 1

        # Usa o serializer recursivo simplificado
        return PlanoAccountRecursivoSerializer(
            subcontas,
            many=True,
            context=new_context
        ).data


class PlanoDeContasRetrieveUpdateModel(serializers.ModelSerializer):
    class Meta:
        model = PlanoAccount
        fields = '__all__'
