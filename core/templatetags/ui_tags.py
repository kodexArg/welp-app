from django import template

register = template.Library()

@register.simple_tag
def active_class(request, url_name, css_class='active'):
    """
    Devuelve una clase CSS si la URL actual coincide con la especificada
    
    Usage: {% active_class request 'core:home' 'text-blue-500' %}
    """
    from django.urls import reverse, resolve
    
    try:
        current_url = resolve(request.path_info).url_name
        target_url = url_name.split(':')[-1] if ':' in url_name else url_name
        
        if current_url == target_url:
            return css_class
    except:
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