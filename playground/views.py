from django.shortcuts import render
from rest_framework.views import APIView
import logging
import requests

# Create your views here.
logger = logging.getLogger(__name__) #__name__相当于playground.views

class HelloView(APIView):
    def get(self, request):
        try:
            logger.info('Calling httpbin')
            response = request.get('https://httpbin.org/delay/2') # 这是一个延迟2s再response的网站
            data = response.json()
            return render(request,'hello.html', {'name': 'll'})
        except requests.ConnectionError:
            logger.critical('httpbin钓线了')
        return render(request, 'hello.html', {'name': 'Mosh'})
'''
最开始使用cache
class HelloView(APIView):
    @method_decorator(cache_page(5*60)) 保存5min
    def get(self, request):
        try:
            logger.info('Calling httpbin')
            response = request.get('https://httpbin.org/delay/2') #
            data = response.json()
            return render(request,'hello.html', {'name': 'll'})
        except requests.ConnectionError:
            logger.critical('httpbin钓线了')
        return render(request, 'hello.html', {'name': 'Mosh'})
'''       