#!/usr/bin/python
#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
import datetime
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from control import usercontrol
from django.views import generic
from spidertool import webtool
from model.user import User
# Create your views here.
def taskdetail(request):
    return render_to_response('nmaptoolview/taskdetail.html', {'data':''})
def indexpage(request):
    islogin = request.COOKIES.get('islogin',False)
    if islogin:
        return render_to_response('nmaptoolview/mainpage.html',{})
    return render_to_response('nmaptoolview/login.html', {'data':''})
def logout(request):
    response= render_to_response('nmaptoolview/login.html', {'data':''})
    webtool.delCookies(response)
    return response
def login(request):
    if request.method=='GET':
        return render_to_response('nmaptoolview/login.html', {'data':''})
    else:
        username=request.POST.get('username','')
        password=request.POST.get('password','')

        result,username,role,power= usercontrol.validuser(username,password)
        if result:
            response = render_to_response('nmaptoolview/mainpage.html', {'data':'用户名和密码成功'})  
            loginuser=User(result,username,password,role,power)
#将username写入浏览器cookie,失效时间为3600

            webtool.setCookies(response,loginuser,3600)

            return response
        else:
            return render_to_response('nmaptoolview/login.html', {'data':'用户名或密码错误'})  

