from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from ticker.serializers import TickerSerializer, TimeSeriesSerializer

class TickerViewSet( ReadOnlyModelViewSet ):
    serializer_class = TickerSerializer
    queryset = TickerSerializer.Meta.model.objects.all()


class TimeSeriesViewSet( ReadOnlyModelViewSet ):
    serializer_class = TimeSeriesSerializer
    queryset = TimeSeriesSerializer.Meta.model.objects.all()

