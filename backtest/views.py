
import json
from django.shortcuts import get_object_or_404, render
from rest_framework import status

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ticker.models import Ticker

from users.models import User
from backtest.models import Backtest

from backtest.strategies.backtesting import backtest

from backtest.serializers import BacktestSerializer
from ticker.serializers import TickerSerializer, TimeSeriesSerializer


class BacktestViewSet( viewsets.GenericViewSet ):
    model = Backtest
    serializer_class = BacktestSerializer
    permission_classes = [IsAuthenticated]
    

    def get_object(self, pk):
        return get_object_or_404( self.model, pk=pk )

    def get_queryset(self, email):
        if self.queryset is None:
            self.queryset = self.model.objects.all()

        # self.queryset = self.model.objects.filter(email=email)
        return self.queryset


    def create(self, request):
        print(request.data )

        user = User.objects.filter( email=request.data.get( 'email' ) ).first()
        ticker = Ticker.objects.filter(symbol=request.data["ticker"]).first()
        margenData = request.data.get('margen')
        margen = None
        for item in Backtest.MARGENS:
            if item[1] == margenData:
                margen = item[0]
        backtest = Backtest(ticker=ticker,capital=request.data["capital"], 
            date_start =request.data["dateStart"], date_end=request.data["dateEnd"], 
            interval=request.data["interval"], indicators_data=request.data["indicatorsData"] ,
            user= user, margen=margen )

        backtest.save()

        return Response(
            {
                'message' : 'Backtest guardado exitosamente!....',
                "data": self.serializer_class(backtest).data
            }, status=status.HTTP_201_CREATED
        )
        """ return Response(
            {
                'message': 'Hay errores en el registro.',
                'errores': user_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST
        ) """

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
        self.model.objects.filter(pk=pk).delete()
        return Response(
                {
                    'message': 'Backtest eliminado correctamente.'
                }, status=status.HTTP_200_OK
            )



class BackTestAPIView( APIView ):
    permission_classes = [IsAuthenticated]


    def post( self, request):
        print( request.data )

        code, resumen, report= backtest( 
            request.data["ticker"], request.data["interval"],
            request.data["capital"], request.data["dateStart"], 
            request.data["dateEnd"], request.data["indicatorsData"],
            request.data["margen"],
        )

        if(code==1):

            data = { "resumen": resumen, "report": report }
            
            return Response(
                {
                    "code": code,
                    'message': 'Backtest Exitoso',
                    "data": data
                },
                status = status.HTTP_200_OK
            )
        if(code==2):
            return Response(
                { "code": code, 'message': 'El ticker seleccionado no posee datos historicos.' },
                status = status.HTTP_200_OK
            )
        if(code==3):
            return Response(
                { "code": code, 'message': 'La configuracion actual no consiguio ningun resultado.' },
                status = status.HTTP_200_OK
            )


class ListBackTestAPIView( APIView ):
    permission_classes = [IsAuthenticated]


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