from django.urls import path
from .views import *
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token # 토큰 획득, 갱신, 확인 추가.

app_name = 'accounts'

urlpatterns = [
    #url('facebook/', FacebookLoginView.as_view(), name='facebook_login'),
    path('users/', UserView.as_view(),name='users'),
    path('validation', ValidationView.as_view(),name='validation'),
    path('signup', signUpView.as_view(),name='signup'),
    path('login', LoginView.as_view(),name='login'),
    path('auth/', obtain_jwt_token),
    path('auth/refresh/', refresh_jwt_token),
    path('auth/verify/',verify_jwt_token),

]