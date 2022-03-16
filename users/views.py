from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import CustomTokenObtainPairSerializer, CustomUserSerializer, UserSerializer, UserListSerializer, UpdateUserSerializer



class Register(APIView):
    def post(self, request):
        user_serializer = UserSerializer( data = request.data )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(
                { 'message': 'Usuario registrado correctamente.'},
                status = status.HTTP_201_CREATED
            )
        print(user_serializer.errors)
        return Response(
            {
                'message': 'Hay errores en el registro.',
                'errors': user_serializer.errors
            },
            status = status.HTTP_400_BAD_REQUEST
        )
        


class Login( TokenObtainPairView ):
    serializer_class = CustomTokenObtainPairSerializer

    def post( self, request, *args, **kwargs ):

        print(request.data)

        email = request.data.get( 'email' )
        password = request.data.get( 'password' )
        user = authenticate( email = email, password = password )
        
        if user:
            login_serializer = self.serializer_class( data = request.data )
            if login_serializer.is_valid():
                user_serializer = CustomUserSerializer( user )
                return Response(
                    {
                        'token':
                            login_serializer.validated_data.get( 'access' ),
                        'refreshToken':
                            login_serializer.validated_data.get( 'refresh' ),
                        'user':
                            user_serializer.data,
                        'message':
                            'Inicio de sesion exitoso.'
                    },
                    status = status.HTTP_200_OK
                )
            return Response(
                { 'error': 'Contraseña o nombre de usuario incorrectos'},
                status = status.HTTP_400_BAD_REQUEST
            )
        return Response(
            { 'error': 'Contraseña o nombre de usuario incorrectos'},
            status = status.HTTP_400_BAD_REQUEST
        )


class Logout( GenericAPIView ):

    def post( self, request, *args, **kwargs ):
        user = User.objects.filter( email = request.data.get( 'email', 0 ) )
        if user.exists():
            RefreshToken.for_user( user.first() )
            return Response(
                { 'message': 'Sesion cerrada correctamente.'},
                status = status.HTTP_200_OK
            )
        return Response(
            { 'error': 'No existe este usuario.'},
            status = status.HTTP_400_BAD_REQUEST
        )


class UserViewSet( GenericViewSet ):
    model = User
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    update_user_serializer = UpdateUserSerializer
    queryset = None

    def get_object(self, pk):
        return get_object_or_404( self.model, pk=pk )

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.model.objects.filter(is_active=True).values('id', 'username', 'email')
        return self.queryset
    
    def list(self, request):
        users = self.get_queryset()
        users_serialzers = self.list_serializer_class(users, many=True)
        return Response( users_serialzers.data, status=status.HTTP_200_OK )


    def create(self, request):
        user_serializer = self.serializer_class( data=request.data )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(
                {
                   'message' : 'Usuario creado correctamente.'
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
                    'message': 'Usuario actualizado correctamente.'
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
                    'message': 'Usuario eliminado correctamente.'
                }, status=status.HTTP_200_OK
            )



