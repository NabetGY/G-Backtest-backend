from django.db import models
from ticker.models import Ticker

from core import settings

class Backtest( models.Model ):

    ONE_BY_ONE = 1
    TWO_BY_ONE = 2
    THREE_BY_ONE = 3
    FOUR_BY_ONE = 4
    FIVE_BY_ONE = 5


    MARGENS = [
        ( ONE_BY_ONE, '1:1' ),
        ( TWO_BY_ONE, '2:1' ),
        ( THREE_BY_ONE, '3:1' ),
        ( FOUR_BY_ONE, '4:1' ),
        ( FIVE_BY_ONE, '5:1' ),
    ]

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete = models.CASCADE
    )

    capital = models.DecimalField("Capital", max_digits=10, decimal_places=2 )
    date_start = models.DateTimeField("Fecha de inicio")
    date_end = models.DateTimeField("Fecha final")
    interval = models.CharField("Intervalo de tiempo", max_length=10)
    indicators_data = models.JSONField("Indicadores")
    margen = models.IntegerField( choices=MARGENS )


    
    



