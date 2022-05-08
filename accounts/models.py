from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import PasswordInput
import datetime
# Create your models here.
class SnsUser(AbstractUser):
    """
    
    id : id 식별자
    password : password
    username : 유저명
    last_login : last_login
    date_joined : date_joined
    is_active : 활성화 여부
    is_superuser : superuser
    facebook : facebook id
    kakao : kakao id
    """
    #facebook = models.CharField(max_length=128,blank=False)
    #kakao = models.CharField(max_length=128, blank=False)

class Sns(models.Model):
    """
    uid : user id
    email : 이메일
    name : 닉네임
    social : sns 종류 (facebook / kakao)
    
    """
    uid = models.ForeignKey('SnsUser', on_delete=models.CASCADE, db_column='uid',default = '')
    email = models.CharField(max_length=128,default = '')
    name = models.CharField(max_length=128,default = '')
    social = models.CharField(max_length=128,default = '')

class SocialToken(models.Model):
    """
    email:email
    social : facebook/kakao
    access_token : access_token
    expiry : 만료
    """
    user= models.CharField(max_length=128,default = '')
    social= models.CharField(max_length=128,default = '')
    access_token = models.CharField(max_length=256,default = '')
    expiry = models.IntegerField(null=True)
    create_at = models.DateTimeField(auto_now_add=True, auto_created=True)

