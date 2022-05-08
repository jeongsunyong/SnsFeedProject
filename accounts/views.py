from django.shortcuts import render
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from rest_framework import permissions, generics, status
from .models import *
from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
import jwt
from django.conf import settings

import requests
import json
import datetime

server_error_return = {'result': False, 'response': {'message': 'Internal Server Error', 'type': 'server'}}
param_error_return = {'result': False, 'response': {'message': 'Parameter is not present', 'type': 'param'}}
exist_error_return = {'result': False, 'response': {'message': 'Parameter is exist', 'type': 'exist'}}
auth_error_return = {'result': False, 'response': {'message': 'AuthenticationException', 'type': 'auth'}}
permission_error_return = {'result': False, 'response': {'message': 'Permission error', 'type': 'permission'}}

#sion_classes = [IsAuthenticated] # JWT 토큰을 사용하기 위한 권한 설정
#authentication_classes = [JSONWebTokenAuthentication] # Authentification을 JWT 방식으로 설정.

# ViewSets define the view behavior.
class UserView(APIView):
    def __init__(self, **kwargs):
        """
        initialize
        """
        pass
        

    @permission_classes((IsAuthenticated))
    @authentication_classes((JSONWebTokenAuthentication,))
    def get(self,request):
        try:
            if 'HTTP_AUTHORIZATION' not in request.META:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=auth_error_return)

            token=request.META['HTTP_AUTHORIZATION'].split(" ")[-1]
            print(token)
            queryset = SnsUser.objects.all()

            print(queryset)
            user=UserSerializer(queryset, many=True).data
            #for u in user[0]:
            #    print(u)

            return_data = {
                "result": True,
                "response": user
            }
            return Response(data=return_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)




# Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
#router.register(r"users", UserViewSet)

class FacebookLoginView(SocialLoginView):
    print("1")
    adapter_class = FacebookOAuth2Adapter
    """"

    return_data = {
            "result": True
    }
    return Response(data=return_data, status=status.HTTP_200_OK)
except Exception as e:
    print(e.__str__())
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)"""

@permission_classes([AllowAny])
class signUpView(APIView):

    def post(self,request):
        try:
            if 'email' not in request.data or 'password' not in request.data or 'social' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=param_error_return)
            email=request.data['email']
            password=request.data['password']
            social=request.data['social']
           
            query_res=SnsUser.objects.filter(username=email)
            if not query_res.exists():
                #신규가입
                user = SnsUser(username=email,password=make_password(password),email=email)
                user.save()
                query_res=SnsUser.objects.filter(username=email)
            uid=query_res.values()[0]['id']


            query_res=Sns.objects.filter(email=social['email'],social=social['social'])
            if not query_res.exists():
                sns=Sns(email=social['email'],name=social['name'],social=social['social'])
                sns.uid = SnsUser.objects.get(id=uid)
                sns.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=param_error_return)


            return_data = {
                        "result": True,
                        "response":'created'
                    }
            return Response(data=return_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)

@permission_classes([AllowAny])
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        try:
            if 'social' in request.data:
                social=request.data['social']
                print(request.data)
                query_res=Sns.objects.filter(email=request.data['username'],social=request.data['social'])
                uid=query_res.values()[0]['uid_id']
                query_res=SnsUser.objects.filter(id=uid)
                if not query_res.exists():
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=auth_error_return)

                print(query_res.values()[0])                
                username=query_res.values()[0]['username']
                token = jwt.encode({'username': username}, settings.SECRET_KEY, algorithm=settings.ALGORITHMS)

                sns_token=request.data['token']

                if request.data['social']=='Facebook': # facebook일경우에는 facebook에서 제공하는 장기토큰 사용.
                    fb_secret=settings.SOCIAL_AUTH_FACEBOOK_SECRET
                    fb_app_id=settings.SOCIAL_AUTH_FACEBOOK_KEY
                    try:
                        url=f'https://graph.facebook.com/v2.10/oauth/access_token?grant_type=fb_exchange_token&client_id= {fb_app_id}&client_secret={fb_secret}&fb_exchange_token={sns_token}'
                        response=requests.get(url)
                        response=response.json()
                        long_token=response['access_token']
                        expiry=response['expires_in']

                        query_res=SocialToken.objects.filter(user=username,social=social)
                        if not query_res.exists():
                            social_token = SocialToken(user=username,social=social,access_token=long_token,expiry=expiry)
                        else :
                            id=query_res.values()[0]['id']
                            social_token = SocialToken(id=id,user=username,social=social,access_token=long_token,expiry=expiry,create_at=datetime.datetime.now())
                        print(social_token)
                        social_token.save()
                    except Exception as e:
                        print(e.__str__())
                        social_token = SocialToken(user=username,social=social,access_token=sns_token)
                        social_token.save()
                elif request.data['social']=='Kakao': # kakao일 경우에는 token에 refresh token을 저장하여 사용.
                    refresh_token=sns_token
                    expiry=request.data['expiry']
                    query_res=SocialToken.objects.filter(user=username,social=social)
                    if not query_res.exists():
                        social_token = SocialToken(user=username,social=social,access_token=refresh_token,expiry=expiry)
                    else :
                        id=query_res.values()[0]['id']
                        social_token = SocialToken(id=id,user=username,social=social,access_token=refresh_token,expiry=expiry,create_at=datetime.datetime.now())
                    social_token.save()
                    """
                    kakao_app_id=settings.SOCIAL_AUTH_KAKAO_KEY 
                    refresh_token=request.data['social']['refresh_token']
                    data={
                        "grant_type": "refresh_token",
                        "client_id": kakao_app_id,
                        "refresh_token": refresh_token
                    }
                    url = "https://kauth.kakao.com/oauth/token"
                    social_token = SocialToken(id=id,user=username,social=social,access_token=long_token,expiry=expiry)"""

                return Response(status=status.HTTP_200_OK,data={
                        "user": username,
                        "token": token
                    })

            else:
                serializer = self.get_serializer(data=request.data)
                if not serializer.is_valid(raise_exception=True):
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=auth_error_return)


                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data
                if user['username'] == "None":
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=auth_error_return)
            
                return Response(status=status.HTTP_200_OK,data={
                        "user": UserSerializer(user, context=self.get_serializer_context()).data, 
                        "token": user['token']
                    })

        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)
class ValidationView(APIView):

    def post(self,request):
        try:
            email=request.data['email']
            social=request.data['social']
            query_res=Sns.objects.filter(email=email ,social=social)
            if query_res.exists():
                result=True
            else:
                result=False

            return_data = {
                        "result": True,
                        "response": {
                            'registered': result
                        }
                    }
            return Response(data=return_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)
