from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def currency_format(value):
    try:
        # Asegúrate de que el valor sea un número y convertirlo a Decimal
        value = Decimal(value)
    except (ValueError, TypeError, InvalidOperation):
        return value  # Devuelve el valor original si no es convertible

    # Formatea el valor como una cadena en formato de moneda
    return f"${value:,.2f}"
