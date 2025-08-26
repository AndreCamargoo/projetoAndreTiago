# utils/atividade_utils.py
from empresa.models import Empresa, Atividade


class AtividadeUtils:
    @staticmethod
    def atualizar_atividade_principal(empresa, nova_principal):
        # 1. Remove principal das outras atividades
        Atividade.objects.filter(empresa=empresa, principal=True).exclude(
            id=nova_principal.id
        ).update(principal=False)

        # 2. Atualiza o campo atividade_principal na empresa
        empresa.atividade_principal = nova_principal.descricao
        empresa.save()

        # 3. Atualiza atividades_secundarias na empresa
        AtividadeUtils.atualizar_atividades_secundarias(empresa)

    @staticmethod
    def atualizar_atividades_secundarias(empresa):
        # Pega todas as atividades não-principais
        secundarias = Atividade.objects.filter(
            empresa=empresa,
            principal=False
        ).values_list('descricao', flat=True)

        # Atualiza o campo na empresa
        empresa.atividades_secundarias = ", ".join(secundarias)
        empresa.save()
