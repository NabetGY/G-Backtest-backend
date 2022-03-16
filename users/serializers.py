from dataclasses import fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User

class CustomTokenObtainPairSerializer( TokenObtainPairSerializer ):
    pass


class CustomUserSerializer( serializers.ModelSerializer ):

    class Meta:
        model = User
        fields = ( 'username', 'email' )


class UserSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UpdateUserSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User
        fields = [ 'username', 'email' ]

    def update(self, instance, validated_data):
        update_user = super().update(instance, validated_data)
        update_user.save()
        return update_user


class UserListSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'username': instance['username'],
            'email': instance['email'],
        }
