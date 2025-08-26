from decimal import Decimal
from django.db import transaction
from empresa.models import Empresa, Socio, Atividade
from datetime import datetime


class CompanySave:
    def __init__(self, responseApi, requestData, user):
        self.requestData = requestData
        self.responseApi = responseApi
        self.user = user

    def processar(self, debug=False):
        with transaction.atomic():
            empresa = self._salvar_empresa()
            self._salvar_socios(empresa)
            self._salvar_atividades(empresa)
            return empresa

    def _salvar_empresa(self):
        # Converte equity para Decimal
        equity = self.responseApi.get('company', {}).get('equity')
        if equity is not None:
            try:
                capital_social = Decimal(str(equity))
            except (ValueError, TypeError):
                capital_social = None
        else:
            capital_social = None

        # Função auxiliar para acessar dados com fallback
        def get_nested(data, keys, default=None):
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current

        # Salvando empresa com dados da API CNPJ
        return Empresa.objects.create(
            user=self.user,
            tipo_documento='PJ',
            documento=get_nested(self.responseApi, ['taxId'], ''),
            nome=get_nested(self.responseApi, ['company', 'name'], ''),
            nome_fantasia=get_nested(self.responseApi, ['alias']),
            data_abertura=get_nested(self.responseApi, ['founded']),
            matriz=get_nested(self.responseApi, ['head'], False),
            status=get_nested(self.responseApi, ['status', 'text'], ''),
            capital_social=capital_social,
            atividade_principal=get_nested(
                self.responseApi, ['mainActivity', 'text']),
            atividades_secundarias=", ".join(
                [activity.get('text', '') for activity in self.responseApi.get('sideActivities', [])]),
            porte=get_nested(self.responseApi, [
                             'company', 'size', 'text'], ''),  # Corrigido aqui
            logradouro=get_nested(self.responseApi, ['address', 'street']),
            numero=get_nested(self.responseApi, ['address', 'number']),
            complemento=get_nested(self.responseApi, ['address', 'details']),
            bairro=get_nested(self.responseApi, ['address', 'district']),
            cidade=get_nested(self.responseApi, ['address', 'city']),
            estado=get_nested(self.responseApi, ['address', 'state']),
            cep=get_nested(self.responseApi, ['address', 'zip']),
            pais=get_nested(self.responseApi, ['address', 'country', 'name']),
            telefone=self._get_phone(),
            email=self._get_email(),
        )

    def _salvar_socios(self, empresa):
        membros = self.responseApi.get('company', {}).get('members', [])
        for membro in membros:
            pessoa = membro.get('person', {})
            Socio.objects.create(
                empresa=empresa,
                nome=pessoa.get('name'),
                cpf=pessoa.get('taxId', '').replace('*', ''),
                funcao=membro.get('role', {}).get('text'),
                data_entrada=self._parse_date(membro.get('since')),
                faixa_etaria=pessoa.get('age')
            )

    def _salvar_atividades(self, empresa):
        main_activity = self.responseApi.get('mainActivity')
        if main_activity:
            Atividade.objects.create(
                empresa=empresa,
                descricao=main_activity.get('text', ''),
                principal=True
            )

        for sec in self.responseApi.get('sideActivities', []):
            Atividade.objects.create(
                empresa=empresa,
                descricao=sec.get('text', ''),
                principal=False
            )

    def _parse_date(self, value):
        if value:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    def _get_phone(self):
        phones = self.responseApi.get("phones", [])
        if phones:
            first = phones[0]
            return f"({first.get('area', '')}) {first.get('number', '')}"
        return None

    def _get_email(self):
        emails = self.responseApi.get("emails", [])
        if emails:
            return emails[0].get("address")
        return None
