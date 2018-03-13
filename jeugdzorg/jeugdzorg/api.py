from .models import Regeling
from rest_framework import routers, serializers, viewsets
from .serializers import RegelingSerializer


# ViewSets define the view behavior.
class RegelingViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    queryset = Regeling.objects.all()
    serializer_class = RegelingSerializer