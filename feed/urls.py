from django.urls import path
from .views import *
from django.conf.urls import url

app_name = 'feed'

urlpatterns = [
    path('renew', RenewView.as_view(),name='renew'),
    path('feedList', PostsView.as_view(),name='feedList'),

]