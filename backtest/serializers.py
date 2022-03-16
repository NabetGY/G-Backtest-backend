import datetime
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


from backtest.models import Backtest

class BacktestSerializer( ModelSerializer ):
    ticker = serializers.SlugRelatedField(
        read_only=True,
        slug_field='symbol'
     )
    class Meta:
        model = Backtest
        fields = '__all__'
