from django.db import models

from accounts.models import User


class Empresa(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('PJ', 'Pessoa Jurídica'),
        ('PF', 'Pessoa Física')
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='empresas', verbose_name="Usuário"
    )
    tipo_documento = models.CharField(
        max_length=2, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo de Documento")
    documento = models.CharField(
        max_length=18, unique=True, verbose_name="CPF/CNPJ")
    nome = models.CharField(
        max_length=255, verbose_name="Nome/Razão Social")
    nome_fantasia = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Nome Fantasia/Alias")
    data_abertura = models.DateField(
        null=True, blank=True, verbose_name="Data de Abertura")
    matriz = models.BooleanField(default=False, verbose_name="É Matriz")
    status = models.CharField(max_length=100, verbose_name="Status da Empresa")
    capital_social = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Capital Social"
    )
    atividade_principal = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Atividade Principal")
    atividades_secundarias = models.TextField(
        null=True, blank=True, verbose_name="Atividades Secundárias")
    porte = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Porte da Empresa")

    # Endereço
    logradouro = models.CharField(max_length=255, verbose_name="Rua/Avenida")
    numero = models.CharField(max_length=20, verbose_name="Número")
    complemento = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=255, verbose_name="Bairro")
    cidade = models.CharField(max_length=255, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    cep = models.CharField(max_length=8, verbose_name="CEP")
    pais = models.CharField(max_length=255, verbose_name="País")

    # Contatos
    telefone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefone")
    email = models.EmailField(null=True, blank=True, verbose_name="E-mail")

    class Meta:
        verbose_name = "Empresa ou Pessoa Física"
        verbose_name_plural = "Empresas e Pessoas Físicas"

    def __str__(self):
        return self.nome


class Socio(models.Model):
    empresa = models.ForeignKey(
        Empresa, related_name='socios', on_delete=models.CASCADE, verbose_name="Empresa"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome do Sócio")
    cpf = models.CharField(max_length=18, verbose_name="CPF do Sócio")
    funcao = models.CharField(max_length=100, verbose_name="Função/Cargo")
    data_entrada = models.DateField(verbose_name="Data de Entrada")
    faixa_etaria = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Faixa Etária")

    class Meta:
        verbose_name = "Sócio"
        verbose_name_plural = "Sócios"

    def __str__(self):
        return f'{self.nome} - {self.funcao}'


class Atividade(models.Model):
    empresa = models.ForeignKey(
        Empresa, related_name='atividades', on_delete=models.CASCADE, verbose_name="Empresa"
    )
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    principal = models.BooleanField(
        default=False, verbose_name="Atividade Principal")

    class Meta:
        verbose_name = "Atividade Econômica"
        verbose_name_plural = "Atividades Econômicas"

    def __str__(self):
        return self.descricao
