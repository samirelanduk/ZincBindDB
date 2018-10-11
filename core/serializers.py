from rest_framework import serializers
from .models import *

class ChainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chain
        exclude = ()



class ChainClusterSerializer(serializers.ModelSerializer):

    chains = ChainSerializer(source="chain_set", many=True)

    class Meta:
        model = ChainCluster
        exclude = ()



class MetalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Metal
        exclude = ()



class AtomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Atom
        exclude = ()



class ResidueSerializer(serializers.ModelSerializer):

    atoms = AtomSerializer(source="atom_set", many=True)

    class Meta:
        model = Residue
        exclude = ()



class ZincSiteSerializer(serializers.ModelSerializer):

    residues = ResidueSerializer(source="residue_set", many=True)
    metals = MetalSerializer(source="metal_set", many=True)

    class Meta:
        model = ZincSite
        exclude = ()



class ZincSiteClusterSerializer(serializers.ModelSerializer):

    zincsites = ZincSiteSerializer(source="zincsite_set", many=True)

    class Meta:
        model = ZincSiteCluster
        exclude = ()



class PdbSerializer(serializers.ModelSerializer):

    zincsites = ZincSiteSerializer(source="zincsite_set", many=True)
    metals = MetalSerializer(source="metal_set", many=True)

    class Meta:
        model = Pdb
        exclude = ()
