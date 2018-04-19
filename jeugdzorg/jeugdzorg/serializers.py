from .models import Regeling
from rest_framework import serializers


class RegelingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Regeling
        fields = (
            'url',
            'titel',
        )
        lookup_field = 'id'
        extra_kwargs = {
            'url': {'lookup_field': 'id'}
        }


class RegelingDetailSerializer(serializers.HyperlinkedModelSerializer):
    voorwaarde_set = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Regeling
        fields = (
            'url',
            'titel',
            'samenvatting',
            'bron',
            'bron_url',
            'aanvraag_url',
            'voorwaarde_set',
        )
        lookup_field = 'id'
        extra_kwargs = {
            'url': {'lookup_field': 'id'},
        }
