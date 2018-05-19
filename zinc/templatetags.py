from django import template

register = template.Library()

@register.filter(name="angstroms")
def angstroms(value):
    """Takes an Angstrom measure - if it is positive it will add units to the
    end, otherwise it will return N/A"""

    return f"{value} Å" if value else "N/A"
