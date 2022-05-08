from django.contrib.auth import authenticate
from .models import *
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings


#class UserSerializer(serializers.HyperlinkedModelSerializer): # rest api로 보여주기 위한 model 변환기. (데이터오브젝트)
#    class Meta:
#        model = SnsUser
#        fields = ["username" ,"is_active"]