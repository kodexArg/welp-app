from django_components import Component, register

@register("nav-link")
class NavLink(Component):
    """Componente para links de navegación en la navbar"""
    
    template_file = "nav-link.html"
    css_file = "nav-link.css"
    js_file = "nav-link.js"
    
    def get_context_data(self, link=None, icon=None, label=None, current_view=None, always_show_label=False, **kwargs):
        """
        Define el contexto que se pasará a la plantilla HTML.
        """
        # Determinar si el link está activo basado en current_view
        active = current_view == link if current_view and link else False
        
        return {
            "link": link,
            "icon": icon,
            "label": label,
            "active": active,
            "always_show_label": always_show_label,
        } 