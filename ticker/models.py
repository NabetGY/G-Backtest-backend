from random import choices
from django.db import models

class Ticker(models.Model):

    name = models.CharField( "Nombre", max_length=255)
    symbol = models.CharField( "Simbolo", max_length=20)
    last_Refreshed = models.DateField(auto_now=True)

    def __str__(self):
        return self.name



class TimeSeries(models.Model):

    INTERVAL_30=1
    INTERVAL_HOUR=2
    INTERVAL_DAY=3

    INTERVALS = [
        ( INTERVAL_30, '30 Minutos' ),
        ( INTERVAL_HOUR, '1 Hora' ),
        ( INTERVAL_DAY, '1 Dia' ),

    ]

    ticker = models.ForeignKey( Ticker, on_delete=models.CASCADE, null=False, blank=False)
    interval = models.IntegerField( choices=INTERVALS )
    
    time = models.DateTimeField()
    open = models.DecimalField( max_digits=11, decimal_places=4 )
    high = models.DecimalField( max_digits=11, decimal_places=4 )
    low = models.DecimalField( max_digits=11, decimal_places=4 )
    close = models.DecimalField( max_digits=11, decimal_places=4 )
    volume = models.DecimalField( max_digits=11, decimal_places=2 )
