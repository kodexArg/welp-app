from django_components import Component, register

@register("separator")
class Separator(Component):
    """Componente para separadores en la navbar"""
    
    template_file = "separator.html"
    css_file = "separator.css"
    js_file = "separator.js"
    
    def get_context_data(self, custom_classes="", **kwargs):
        """
        Define el contexto que se pasará a la plantilla HTML.
        """
        return {
            "custom_classes": custom_classes,
        } 