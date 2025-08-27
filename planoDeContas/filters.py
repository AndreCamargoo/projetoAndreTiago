import django_filters

from django.db.models import Q

from .models import PlanoAccount


class PlanoDeContasFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_by_q', label="Pesquisar")

    class Meta:
        model = PlanoAccount
        fields = []

    def filter_by_q(self, queryset, name, value):
        if not value:
            return queryset

        # Filtra os campos com base no valor de 'q'
        return queryset.filter(
            Q(nome__icontains=value) |
            Q(codigo__icontains=value) |
            Q(tipo__icontains=value) |
            Q(descricao__icontains=value) |
            Q(empresa__documento__icontains=value) |
            Q(empresa__nome__icontains=value) |
            Q(vinculo__codigo__icontains=value) |
            Q(cadastrado_em__icontains=value) |
            Q(atualizado_em__icontains=value)
        )
