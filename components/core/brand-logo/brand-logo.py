from django_components import Component, register

@register("brand-logo")
class BrandLogo(Component):
    template_file = "brand-logo.html"
    css_file = "brand-logo.css"
    js_file = "brand-logo.js"
    
    def get_context_data(self, show_text=True, **kwargs):
        return {
            "show_text": show_text
        } 