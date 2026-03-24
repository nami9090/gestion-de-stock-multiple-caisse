from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplie value par arg"""
    return value * arg