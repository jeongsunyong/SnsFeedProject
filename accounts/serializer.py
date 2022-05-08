from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *
from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings

# JWT 사용을 위한 설정
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class UserSerializer(serializers.HyperlinkedModelSerializer): # rest api로 보여주기 위한 model 변환기. (데이터오브젝트)
    class Meta:
        model = SnsUser
        fields = ["username" ,"is_active"]

class SnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sns
        fields = ["uid","name","email","social"]
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialToken
        fields = ["user","social","access_token","expiry"]
        
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password", None)

        user = authenticate(username=username, password=password)

        if user is None:
            return {'username': 'None'}
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given username and password does not exist'
            )
        return {
            'username': user.username,
            'token': jwt_token
        }
