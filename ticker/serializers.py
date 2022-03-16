from datetime import datetime, timezone
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


from ticker.models import Ticker, TimeSeries

class TickerSerializer( ModelSerializer ):
    
    class Meta:
        model = Ticker
        fields = '__all__'


class TimestampField(serializers.Field):
    def to_representation(self, value):
        newValue= value.replace(tzinfo=timezone.utc)
        return newValue.timestamp()

class TimeSeriesSerializer( ModelSerializer ):
    time = TimestampField()
    class Meta:
        model = TimeSeries
        fields = '__all__'

