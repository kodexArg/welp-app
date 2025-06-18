from django_components import Component, register

@register("logout")
class Logout(Component):
    """Componente para el logout en la navbar"""
    
    template_file = "logout.html"
    css_file = "logout.css"
    js_file = "logout.js"
    
    def get_context_data(self, **kwargs):
        """
        Define el contexto que se pasará a la plantilla HTML.
        """
        return {}
    
    class Media:
        css = ["core/logout/logout.css"]
        js = ["core/logout/logout.js"] 