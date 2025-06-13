from django_components import Component, register

@register("ping")
class Ping(Component):
    """Componente simple para demostrar django-components"""
    
    template_name = "ping.html"
    
    def get_context_data(self, ping=None, **kwargs):
        """
        Define el contexto que se pasará a la plantilla HTML.
        Los argumentos de esta función son los 'props' que recibe el componente.
        """
        return {
            "response": "PONG" if ping else "No ping",
            "has_ping": bool(ping),
            "ping_value": ping,
        }
    
    class Media:
        css = ["core/ping/ping.css"]
        js = ["core/ping/ping.js"] 