from django.db import models

from empresa.models import Empresa


class Fornecedores(models.Model):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name='fornecedores', verbose_name="Empresa"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome")
    documento = models.CharField(
        max_length=20, unique=True, verbose_name="CPF/CNPJ")

    # Endereço
    logradouro = models.CharField(max_length=255, verbose_name="Rua/Avenida")
    numero = models.CharField(max_length=20, verbose_name="Número")
    complemento = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=255, verbose_name="Bairro")
    cidade = models.CharField(max_length=255, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    cep = models.CharField(max_length=10, verbose_name="CEP")
    pais = models.CharField(max_length=255, verbose_name="País")

    telefone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefone")
    celular = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(
        max_length=255, unique=True, null=True, blank=True, verbose_name="E-mail")
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização")

    def __str__(self):
        return f'{self.nome} - {self.documento}'
