from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class RegelingViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = ()
    queryset = Regeling.objects.all()
    serializer_class = RegelingSerializer
    lookup_field = ('id')

    def list(self, request):
        serializer_context = {
            'request': request,
        }
        queryset = Regeling.objects.all()
        serializer = RegelingSerializer(queryset, many=True, context=serializer_context)
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        serializer_context = {
            'request': request,
        }
        queryset = Regeling.objects.all()
        regeling = get_object_or_404(queryset, id=id)
        serializer = RegelingDetailSerializer(regeling, context=serializer_context)
        return Response(serializer.data)