from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated


from ticker.serializers import TickerSerializer, TimeSeriesSerializer

class TickerViewSet( ReadOnlyModelViewSet ):
    permission_classes = [IsAuthenticated]
    serializer_class = TickerSerializer
    queryset = TickerSerializer.Meta.model.objects.all()


class TimeSeriesViewSet( ReadOnlyModelViewSet ):
    permission_classes = [IsAuthenticated]
    serializer_class = TimeSeriesSerializer
    queryset = TimeSeriesSerializer.Meta.model.objects.all()

