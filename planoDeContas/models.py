from django.db import models

from empresa.models import Empresa


class PlanoAccount(models.Model):
    TIPO_CHOICES = (
        ("A", "Analítica"),
        ("S", "Sintética"),
    )

    empresa = models.ForeignKey(
        Empresa, related_name='planos_contas', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    descricao = models.TextField()
    vinculo = models.ForeignKey(
        'self', blank=True, null=True, related_name='subcontas', on_delete=models.CASCADE)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.codigo} - {self.nome}'
