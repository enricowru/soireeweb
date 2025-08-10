from django import template

register = template.Library()

@register.filter
def format_k(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        else:
            return str(value)
    except (ValueError, TypeError):
        return "0"
