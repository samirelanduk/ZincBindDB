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


def specific_search(title=None, organism=None, code=None, **kwargs):
    qs = []
    if title is not None:
        qs.append(Q(pdb__title__contains=title[0].upper()))
    if organism is not None:
        qs.append(Q(pdb__organism__contains=organism[0].upper()))
    if code is not None:
        qs.append(Q(pdb__id__contains=code[0].upper()))
    results = ZincSite.objects.filter(*qs).order_by("-pdb__deposited")
    return results
