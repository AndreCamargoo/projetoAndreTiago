import re
from app.utils.exceptions import ValidationError


def validate_cpf_cnpj(value):
    """
    Valida se o valor fornecido é um CPF ou CNPJ válido.
    Lança uma exceção do tipo ValidationError caso o CPF ou CNPJ seja inválido.
    """

    # Remover caracteres não numéricos
    value_cleaned = re.sub(r"[^0-9]", "", value)

    # Verifica se é CPF ou CNPJ
    if len(value_cleaned) == 11:  # CPF
        if not is_valid_cpf(value_cleaned):
            raise ValidationError("Invalid CPF.")
    elif len(value_cleaned) == 14:  # CNPJ
        if not is_valid_cnpj(value_cleaned):
            raise ValidationError("Invalid CNPJ.")
    else:
        raise ValidationError("Invalid CPF or CNPJ.")


def is_valid_cpf(cpf):
    """
    Valida CPF com base nos algoritmos de verificação.
    """
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * len(cpf):
        return False

    def calc_digit(digits):
        s = sum(int(digit) * weight for digit,
                weight in zip(digits, range(len(digits) + 1, 1, -1)))
        remainder = 11 - s % 11
        return str(remainder) if remainder < 10 else '0'

    if cpf[-2:] == calc_digit(cpf[:-2]) + calc_digit(cpf[:-1]):
        return True

    return False


def is_valid_cnpj(cnpj):
    """
    Valida CNPJ com base nos algoritmos de verificação.
    """
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * len(cnpj):
        return False

    def calc_digit(digits, weights):
        s = sum(int(digit) * weight for digit, weight in zip(digits, weights))
        remainder = s % 11
        return str(11 - remainder if remainder > 1 else 0)

    first_digit_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_digit_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    if cnpj[-2:] == calc_digit(cnpj[:-2], first_digit_weights) + calc_digit(cnpj[:-1], second_digit_weights):
        return True

    return False
