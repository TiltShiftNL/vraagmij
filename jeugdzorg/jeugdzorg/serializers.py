from django.conf.urls import url, include
from .models import Regeling
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class RegelingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Regeling
        fields = ('titel', )
