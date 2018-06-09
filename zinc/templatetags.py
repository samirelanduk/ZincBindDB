from django import template

register = template.Library()

@register.filter(name="angstroms")
def angstroms(value):
    """Takes an Angstrom measure - if it is positive it will add units to the
    end, otherwise it will return N/A"""

    return f"{value} Å" if value else "N/A"


@register.filter(name="pagify")
def pagify(url, page):
    """Takes a URL and adds a page number to it"""

    return url[:-1] + str(page) if "page" in url else url + f"&page={page}"
