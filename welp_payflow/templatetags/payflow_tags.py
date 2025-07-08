from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('components/welp_payflow/radio-button.html')
def radio_button(target, id, label, next_target, visible=True):
    """Componente radio-button HTMX usado en Welp Payflow."""
    try:
        full_url = reverse(f'welp_payflow:htmx-{next_target}', kwargs={target: id})
    except Exception:
        full_url = ''

    return {
        'target': target,
        'id': id,
        'label': label,
        'next_target': next_target,
        'full_url': full_url,
        'visible': visible,
    } 