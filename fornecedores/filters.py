import django_filters

from django.db.models import Q

from .models import Fornecedores


class FornecedorFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_by_q', label="Pesquisar")

    class Meta:
        model = Fornecedores
        fields = []

    def filter_by_q(self, queryset, name, value):
        if not value:
            return queryset

        # Filtra os campos com base no valor de 'q'
        return queryset.filter(
            Q(nome__icontains=value) |
            Q(documento__icontains=value) |
            Q(logradouro__icontains=value) |
            Q(cidade__icontains=value) |
            Q(empresa__documento__icontains=value) |
            Q(empresa__nome__icontains=value) |
            Q(data_criacao__icontains=value) |
            Q(data_atualizacao__icontains=value)
        )
