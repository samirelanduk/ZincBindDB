from .models import ZincSite

def omni_search(term):
    results = ZincSite.objects.filter(id__contains=term.upper())
    return results
