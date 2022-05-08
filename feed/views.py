from django.shortcuts import render


from rest_framework import permissions, generics, status
from .models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializer import *

from django.conf import settings

import requests
import json
import datetime
from accounts.models import SnsUser
from accounts.models import Sns
from elasticsearch import helpers
from elasticsearch import Elasticsearch


server_error_return = {'result': False, 'response': {'message': 'Internal Server Error', 'type': 'server'}}
param_error_return = {'result': False, 'response': {'message': 'Parameter is not present', 'type': 'param'}}
exist_error_return = {'result': False, 'response': {'message': 'Parameter is exist', 'type': 'exist'}}
auth_error_return = {'result': False, 'response': {'message': 'AuthenticationException', 'type': 'auth'}}
permission_error_return = {'result': False, 'response': {'message': 'Permission error', 'type': 'permission'}}

es = Elasticsearch(hosts=[settings.ES_HOST],verify_certs=False,headers={"Content-Type" : "application/json"})
#es=Elasticsearch(scheme='https://',host=settings.ES_HOST,port=settings.ES_PORT)
index='sns_posts'

@authentication_classes((JSONWebTokenAuthentication,))
class RenewView(APIView):

    def post(self,request):
        try:
            if 'HTTP_AUTHORIZATION' not in request.META:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=auth_error_return)

            id,name,email,social,token = request.data.values()
            query_res=Sns.objects.filter(social=social, email=email)
            print(query_res.values()[0])
            uid=query_res.values()[0]['uid_id']

            query_res=SnsUser.objects.filter(id=uid)
            username=query_res.values()[0]['username']

            if social=='Facebook':
                url=f'https://graph.facebook.com/v13.0/{id}/feed?access_token={token}&limit=1000'
                response=requests.get(url)
                response=response.json()
                datas=response['data']
                bulk_actions=[]
                for data in datas:
                    if 'message' in data or 'img_url' in data:
                        source={
                            "user":username,
                            "img_url":data['img_url'] if "img_url" in data else "",
                            "content":data['message'] if "message" in data else "",
                            "writer":"",
                        }
                        bulk_actions.append({
                            "_id":data["id"],
                            "_index":index,
                            "doc":source,
                            "_op_type":"update",
                            "doc_as_upsert":True
                        })
                helpers.bulk(es, bulk_actions)

            elif social=='Kakao':
                pass

            return_data = {
                        "result": True,
                        "response":"renew_data"
                    }
            return Response(data=return_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)



@authentication_classes((JSONWebTokenAuthentication,))
class PostsView(APIView):

    def get(self,request):
        try:
            if 'HTTP_AUTHORIZATION' not in request.META:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=auth_error_return)

            email=request.query_params.get('email')
            social=request.query_params.get('social')
            keyword=request.query_params.get('keyword')
            print(email,social,keyword)
            query_res=Sns.objects.filter(social=social, email=email)
            print(query_res)
            uid=query_res.values()[0]['uid_id']

            query_res=SnsUser.objects.filter(id=uid)
            username=query_res.values()[0]['username']
            size=100#tmp
            query = {
                "size": size,
                "query":{
                    "bool": {
                        "must": [{
                        "match_phrase":{
                            "user":username
                        }
                    }]}
                }
            }

            if keyword=='':
                query['query']['bool']['must'].append({
                    "match":{
                        "content.ngram":keyword
                    }
                })

            result = es.search(index=index, body=query)
            if len(result) <= 0:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)
            
            source=[]
            for res in result['hits']['hits']:
                source.append(res['_source'])
            return_data = {
                        "result": True,
                        "response":source
                    }

            return Response(data=return_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=server_error_return)
