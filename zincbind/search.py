from itertools import chain
from django.db.models import Q
from .models import ZincSite

def omni_search(term):
    results = ZincSite.objects.filter(
     Q(id__contains=term.upper()) | Q(pdb__title__contains=term.upper()) |
     Q(pdb__organism__contains=term.upper()) | Q(pdb__expression__contains=term.upper()) |
     Q(pdb__technique__contains=term.upper()) | Q(pdb__classification__contains=term.upper())
    ).order_by("-pdb__deposited")
    return results


def specific_search(title=None, **kwargs):
    results = ZincSite.objects.filter(
     Q(pdb__title__contains=title[0].upper())
    ).order_by("-pdb__deposited")
    return results
