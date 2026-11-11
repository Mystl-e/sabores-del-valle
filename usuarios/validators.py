import re

from django.core.exceptions import ValidationError


def validar_rut(valor):
    rut = valor.strip().upper()
    if not re.fullmatch(r'\d{7,8}-[\dK]', rut):
        raise ValidationError('Formato de RUT inválido. Use 12345678-9 (sin puntos y con guion).')

    cuerpo, dv = rut.split('-')
    suma, factor = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1

    resto = 11 - (suma % 11)
    dv_esperado = {11: '0', 10: 'K'}.get(resto, str(resto))
    if dv != dv_esperado:
        raise ValidationError('El dígito verificador del RUT no es válido.')