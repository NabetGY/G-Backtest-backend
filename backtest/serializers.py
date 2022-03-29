import datetime
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


from backtest.models import Backtest


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key


class BacktestSerializer( ModelSerializer ):
    ticker = serializers.SlugRelatedField(
        read_only=True,
        slug_field='symbol'
     )

    margen = ChoiceField(choices=Backtest.MARGENS)
    class Meta:
        model = Backtest
        fields = '__all__'
