from django.db import models
from ticker.models import Ticker

from core import settings

class Backtest( models.Model ):

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete = models.CASCADE
    )
    capital = models.DecimalField("Capital", max_digits=10, decimal_places=2 )
    date_start = models.DateTimeField("Fecha de inicio")
    date_end = models.DateTimeField("Fecha final")
    interval = models.CharField("Intervalo de tiempo", max_length=10)
    indicators_data = models.JSONField("Indicadores")


    
    



