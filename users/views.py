from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from users.models import User
from users.serializers import  CustomUserSerializer, UserSerializer, UserListSerializer, UpdateUserSerializer



class Register(GenericAPIView):
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
        


class Login( ObtainAuthToken ):

    def post(self,request,*args,**kwargs):
        # send to serializer email and password
        email = request.data.get( 'email' )
        password = request.data.get( 'password' )
        user = authenticate( email = email, password = password )
        if user:
            if user.is_active:
                token,created = Token.objects.get_or_create(user = user)
                user_serializer = CustomUserSerializer(user)
                if created:
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    }, status = status.HTTP_201_CREATED)
                else:
                    """
                    all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                    if all_sessions.exists():
                        for session in all_sessions:
                            session_data = session.get_decoded()
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                    
                    token = Token.objects.create(user = user)
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    }, status = status.HTTP_201_CREATED)
                    """
                    token.delete()
                    return Response({
                        'error': 'Ya se ha iniciado sesión con este usuario.'
                    }, status = status.HTTP_409_CONFLICT)
            else:
                return Response({'error':'Este usuario no puede iniciar sesión.'}, 
                                    status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Nombre de usuario o contraseña incorrectos.'},
                                    status = status.HTTP_400_BAD_REQUEST)
        return Response({'mensaje':'Hola desde response'}, status = status.HTTP_200_OK)


class Logout(GenericAPIView):

    def post(self,request,*args,**kwargs):
        try:
            token = request.data.get('token')
            token = Token.objects.filter(key = token).first()

            if token:
                user = token.user

                # delete all sessions for user
                all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        # search auth_user_id, this field is primary_key's user on the session
                        if user.id == int(session_data.get('_auth_user_id')):
                            session.delete()

                # delete user token
                token.delete()

                session_message = 'Sesiones de usuario eliminadas.'  
                token_message = 'Token eliminado.'

                return Response({'token_message': token_message,'session_message':session_message},
                                    status = status.HTTP_200_OK)
            
            return Response({'error':'No se ha encontrado un usuario con estas credenciales.'},
                    status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'No se ha encontrado token en la petición.'}, 
                                    status = status.HTTP_409_CONFLICT)




class UserViewSet( GenericViewSet ):
    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    update_user_serializer = UpdateUserSerializer
    queryset = None
    lookup_field = 'email'
    lookup_url_kwarg = 'email'
    lookup_value_regex = '[\w@.]+' 
    

    def get_object(self, email):
        return get_object_or_404( self.model, email=email )

    def get_queryset( self ):
        if self.queryset is not None:
            self.queryset = self.model.objects.filter( is_active = True )
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

    def retrieve( self, request, email=None ):
        user = self.get_object( email )
        user_serializer = self.serializer_class( user )
        return Response( user_serializer.data )

    def update( self, request,pk=None, email=None ):
        print('enttre a la actualizacion')
        user = self.get_object( email )
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
    
    def destroy( self, request, email=None ):
        self.model.object.filter(email=1).delete()
        return Response(
                {
                    'message': 'Usuario eliminado correctamente.'
                }, status=status.HTTP_200_OK
            )



class UserUpdateAPIView( GenericAPIView ):
    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UpdateUserSerializer

    def get_object(self, email):
        return get_object_or_404( self.model, email=email )

    def get_queryset( self ):
        if self.queryset is not None:
            self.queryset = self.model.objects.filter( is_active = True )
        return self.queryset
    
    def post( self, request, email=None ):
        print("entro")
        email = request.data.get( 'email' )
        username = request.data.get( 'username' )
        user = self.get_object( email )
        user_serializer = self.serializer_class( user, data=request.data )
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


class UserDeleteAPIView( GenericAPIView ):
    permission_classes = [IsAuthenticated]
    model = User

    def get_object(self, email):
        return get_object_or_404( self.model, email=email )
    
    def post( self, request, email=None ):
        email = request.data.get( 'email' )
        user = self.get_object( email )
        print(user)
        user.delete()
        return Response(
            {
                'message': 'Cuenta elimininada correctamente.'
            }, status=status.HTTP_200_OK
        )

