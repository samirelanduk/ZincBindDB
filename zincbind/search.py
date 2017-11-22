from itertools import chain
from django.db.models import Q
from .models import ZincSite

def omni_search(term):
    '''id_results = ZincSite.objects.filter(id__contains=term.upper()).order_by("-pdb__deposited")
    title_results = ZincSite.objects.filter(pdb__title__contains=term.upper())
    return list(chain(id_results, title_results))'''

    results = ZincSite.objects.filter(
     Q(id__contains=term.upper()) | Q(pdb__title__contains=term.upper()) |
     Q(pdb__organism__contains=term.upper()) | Q(pdb__expression__contains=term.upper()) |
     Q(pdb__technique__contains=term.upper()) | Q(pdb__classification__contains=term.upper())
    ).order_by("-pdb__deposited")
    return results
