from django.contrib import admin

from ticker.models import Ticker, TimeSeries

admin.site.register(Ticker)
admin.site.register(TimeSeries)

