from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html

register = template.Library()

@register.simple_tag(takes_context=True)
def active_class(context, view_name, class_name='active'):
    """
    Devuelve una clase CSS si la URL actual coincide con la especificada
    
    Usage: {% active_class request 'core:index' 'text-blue-500' %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    try:
        current_url = reverse(view_name)
        target_url = view_name.split(':')[-1] if ':' in view_name else view_name
        
        if current_url == target_url:
            return class_name
    except NoReverseMatch:
        pass
    
    return ''

@register.filter
def add_class(field, css_class):
    """
    Agrega clases CSS a un campo de formulario
    
    Usage: {{ form.field|add_class:"form-input" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field

