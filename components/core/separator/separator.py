from django_components import Component, register

@register("separator")
class Separator(Component):
    """Componente para separadores en la navbar"""
    
    template_name = "separator.html"
    
    def get_context_data(self, custom_classes="", **kwargs):
        """
        Define el contexto que se pasará a la plantilla HTML.
        """
        return {
            "custom_classes": custom_classes,
        }
    
    class Media:
        css = ["core/separator/separator.css"]
        js = ["core/separator/separator.js"] 