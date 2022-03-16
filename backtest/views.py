
import json
from django.shortcuts import get_object_or_404, render
from rest_framework import status

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from backtest.models import Backtest

from backtest.strategies.backtesting import backtest

from backtest.serializers import BacktestSerializer
from ticker.serializers import TickerSerializer, TimeSeriesSerializer


class BacktestViewSet( viewsets.GenericViewSet ):
    model = Backtest
    serializer_class = BacktestSerializer
    

    def get_object(self, pk):
        return get_object_or_404( self.model, pk=pk )

    def get_queryset(self, email):
        if self.queryset is None:
            self.queryset = self.model.objects.all()

        # self.queryset = self.model.objects.filter(email=email)
        return self.queryset


    def create(self, request):
        user_serializer = self.serializer_class( data=request.data )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(
                {
                   'message' : 'Backtest creado correctamente.'
                }, status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Hay errores en el registro.',
                'errores': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )

    def retrieve( self, request, pk=None ):
        user = self.get_object( pk )
        user_serializer = self.serializer_class( user )
        return Response( user_serializer.data )

    def update( self, request, pk=None ):
        user = self.get_object( pk )
        user_serializer = self.update_user_serializer( user, data=request.data )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(
                {
                    'message': 'Backtest actualizado correctamente.'
                }, status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Hay errores en la actualizacion.',
                'errores': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy( self, request, pk=None ):
        self.model.object.filter(pk=1).delete()
        return Response(
                {
                    'message': 'Backtest eliminado correctamente.'
                }, status=status.HTTP_200_OK
            )



class BackTestAPIView( APIView ):

    def post( self, request):
        print( request.data )

        resumen, report, timeSerie= backtest( 
            request.data["ticker"], 
            request.data["capital"], request.data["dateStart"], 
            request.data["dateEnd"], request.data["indicatorsData"],
            request.data.get( 'email' )
        )

        
        timeSerieSerializer = TimeSeriesSerializer(timeSerie, many=True)
        data = {
            "resumen": resumen,
            "report": report,
            "data": timeSerieSerializer.data
        }
        
        return Response(
                { 
                    'message': 'llegaron los datos',
                    "data": data
                },
                status = status.HTTP_200_OK
            )


class ListBackTestAPIView( APIView ):

    model = Backtest
    serializer_class = BacktestSerializer
    queryset = None

    def get_queryset(self, email):
        if self.queryset is None:
            user = User.objects.filter(email=email).first()
            self.queryset = self.model.objects.filter(user=user)
        return self.queryset

    def post( self, request):
        backtests = self.get_queryset( request.data.get('email') )
        backtests_serialzers = self.serializer_class(backtests, many=True)
        return Response( backtests_serialzers.data, status=status.HTTP_200_OK )