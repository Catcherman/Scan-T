#!/usr/bin/python
#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseNotFound
import datetime
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from nmaptoolbackground.control import usercontrol,jobcontrol,ipcontrol,portcontrol,taskcontrol
from django.views import generic
from spidertool import webtool
from fontsearch.control import mapcontrol
import json

timeout=60*20
                
def indexpage(request):
    username = request.COOKIES.get('username','')
    return render_to_response('fontsearchview/search.html', {'data':'','username':username})
def mainpage(request):
    content=request.GET.get('searchcontent','')

    page=request.GET.get('page','0')
    username = request.COOKIES.get('username','')
    content=content.replace(' ','%20')
    return render_to_response('fontsearchview/searchdetail.html', {'data':content,'page':page,'username':username})
def mapsearchmain(request):
    username = request.COOKIES.get('username', '')
    return render_to_response('fontsearchview/mapsearchmain.html',{'username':username})
def detailpage(request):
    from spidertool import redistool, webtool
    content=request.POST.get('content','')
    print content
    page=request.POST.get('page','0')
    username = request.COOKIES.get('username','')
    response_data = {}  
    response_data['result'] = '0'
    jsoncontent=None
    ports=None
    import json
    try:
        jsonmsg='{'+content+'}'
        jsoncontent=json.loads(jsonmsg)
    except Exception,e:
        print e
        pass

    if jsoncontent is None:
    
        if  content!='' and len(content)>0:
            print '存在内容，进入elasticsearch 检索'
#         extra='    or   script  like \'%'+content+'%\' or detail  like \'%'+content+'%\'  or timesearch like ' +'\'%'+content+'%\' or head like \'%' +content+'%\') and  snifferdata.ip=ip_maindata.ip '
#         ports,portcount,portpagecount=portcontrol.portabstractshow(ip=content,port=content,timesearch=content,state=content,name=content,product=content,version=content,page=page,extra=extra,command='or')
            try:

                item=webtool.md5('sch_'+str(content)+'page'+str(page))

                redisresult = redistool.get(str(item))

                if redisresult :
                    print '从redids取的数据'
                    try:
                        response_data['result'] = '1'

                        response_data['ports'] = redisresult['ports']
                        response_data['portslength'] = redisresult['portslength']

                        response_data['portspagecount'] = redisresult['portspagecount']
                        response_data['portspage'] = redisresult['portspage']
                    except Exception,e:
                        import sys
                        sys.path.append("..")
                        from elasticsearchmanage import elastictool
                        ports, portcount, portpagecount = elastictool.search(page=page, dic=None, content=content)

                        redisdic = {}
                        redisdic['ports'] = ports
                        redisdic['portslength'] = portcount
                        redisdic['portspagecount'] = portpagecount
                        redisdic['portspage'] = page
                        redistool.set(item, redisdic)
                        redistool.expire(item, timeout)
                        response_data['ports'] = ports
                        response_data['portslength'] = portcount
                        response_data['portspagecount'] = portpagecount
                        response_data['portspage'] = page


                else:
                    import sys
                    sys.path.append("..")
                    from elasticsearchmanage import elastictool
                    ports,portcount,portpagecount=elastictool.search(page=page,dic=None,content=content)

                    redisdic = {}

                    redisdic['ports'] = ports
                    redisdic['portslength'] = portcount
                    redisdic['portspagecount'] = portpagecount
                    redisdic['portspage'] = page
                    redistool.set(item, redisdic)
                    redistool.expire(item, timeout)
                    response_data['ports'] = ports
                    response_data['portslength'] = portcount
                    response_data['portspagecount'] = portpagecount
                    response_data['portspage'] = page

#             extra='     where     match(version,product,head,detail,script,hackinfo,disclosure,keywords) against(\''+content+'\' in Boolean mode)  '

#             ports,portcount,portpagecount=portcontrol.portabstractshow(page=page,extra=extra,command='or')
            except Exception,e:
                print e
                try:
                    ports, portcount, portpagecount = getattr(portcontrol, 'portabstractshow', 'portabstractshow')(**jsoncontent)
                    response_data['ports'] = ports
                    response_data['portslength'] = portcount
                    response_data['portspagecount'] = portpagecount
                    response_data['portspage'] = page
                except Exception,e:
                    print e
            print '检索完毕'
            response_data['result'] = '1'

            response_data['keywords'] = content.split()

            response_data['username']=username
    else:
        action=jsoncontent.keys()
        if 'use' in action or 'city' in action:
            del jsoncontent['use']
            jsoncontent['page']=page
            if 'all' in action:
                
                extra='     where     match(version,product,head,detail,script,hackinfo,disclosure,keywords) against(\''+jsoncontent['all']+'\' in Boolean mode)  '

                ports,portcount,portpagecount=portcontrol.portabstractshow(page=page,extra=extra,command='or')

            else:
        
                ports,portcount,portpagecount=getattr(portcontrol, 'portabstractshow','portabstractshow')(**jsoncontent)
            response_data['result'] = '1'
            response_data['keywords'] = jsoncontent.values()
            response_data['ports']=ports
            response_data['portslength']=portcount
            response_data['portspagecount']=portpagecount
            response_data['portspage']=page
            response_data['username']=username
        else:
            if len(content)==0:
                return HttpResponse(json.dumps(response_data,skipkeys=True,default=webtool.object2dict), content_type="application/json")  
 
            print '进入elasticsearch 具体关键词匹配'
            try:
                item =str(webtool.md5('sch_' + str(jsoncontent) + '_page' + str(page)))
                print item
                redisresult = redistool.get(item)
                if redisresult:
                    print '从redids取的数据'
                    try:
                        response_data['result'] = '1'

                        response_data['ports'] = redisresult['ports']
                        response_data['portslength'] = redisresult['portslength']

                        response_data['portspagecount'] = redisresult['portspagecount']
                        response_data['portspage'] = redisresult['portspage']
                    except Exception,e:
                        import sys
                        sys.path.append("..")
                        from elasticsearchmanage import elastictool
                        ports, portcount, portpagecount = elastictool.search(page=page, dic=jsoncontent, content=None)

                        response_data['ports'] = ports
                        response_data['portslength'] = portcount
                        response_data['portspagecount'] = portpagecount
                        response_data['portspage'] = page

                        redisdic = {}
                        redisdic['ports'] = ports
                        redisdic['portslength'] = portcount
                        redisdic['portspagecount'] = portpagecount
                        redisdic['portspage'] = page
                        redistool.set(item, redisdic)
                        redistool.expire(item, timeout)


                else:
                    import sys
                    sys.path.append("..")
                    from elasticsearchmanage import elastictool
                    ports,portcount,portpagecount=elastictool.search(page=page,dic=jsoncontent,content=None)
                    print '设置返回值'

                    response_data['ports'] = ports
                    response_data['portslength'] = portcount
                    response_data['portspagecount'] = portpagecount
                    response_data['portspage'] = page


                    redisdic = {}
                    redisdic['ports'] = ports
                    redisdic['portslength'] = portcount
                    redisdic['portspagecount'] = portpagecount
                    redisdic['portspage'] = page
                    print '准备存入redis'
                    redistool.set(item, redisdic)
                    redistool.expire(item, timeout)
                    print '存入redis'

            except Exception,e:
                print e,206
                ports, portcount, portpagecount = getattr(portcontrol, 'portabstractshow', 'portabstractshow')(**jsoncontent)
                response_data['ports']=ports
                response_data['portslength']=portcount
                response_data['portspagecount']=portpagecount
                response_data['portspage']=page

            response_data['result'] = '1'
            response_data['keywords'] = jsoncontent.values()

            response_data['username']=username

    try:

        return HttpResponse(json.dumps(response_data,skipkeys=True,default=webtool.object2dict), content_type="application/json")
    except Exception,e:
        print e
        return HttpResponse(json.dumps(response_data,skipkeys=True,default=webtool.object2dict,encoding='latin-1'), content_type="application/json")


        # return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict, encoding='GB2312'),
        #             content_type="application/json")

    
def mapsearch(request):
    from spidertool import redistool,webtool
    content = request.POST.get('content', '')
    username = request.COOKIES.get('username', '')
    response_data = {}
    response_data['result'] = '0'
    jsoncontent = None
    ports = None
    import json
    try:
        jsonmsg = '{' + content + '}'
        jsoncontent = json.loads(jsonmsg)
    except Exception, e:
        print e
        pass

    if jsoncontent is None or jsoncontent =={}:
        redisresult=redistool.get(content)
        if redisresult:
            print '从redids取的数据'

            response_data['result'] = '1'

            response_data['ports'] = redisresult['ports']
            response_data['portslength'] = redisresult['portslength']
            response_data['resultsize'] = redisresult['resultsize']


        else:
            ports,portcount,resultsize=mapcontrol.mapshow(searchcontent=content, isdic=0)
            redisdic={}
            redisdic['ports'] = ports
            redisdic['portslength'] = portcount
            redisdic['resultsize'] = resultsize
            redistool.set(content,redisdic)

            response_data['result'] = '1'

            response_data['ports'] = ports
            response_data['portslength'] = portcount
            response_data['resultsize'] = resultsize

        response_data['username'] = username
    else:
        action = jsoncontent.keys()

        if len(content) == 0:
            return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict),
                                    content_type="application/json")

        redisresult = redistool.get(webtool.md5(str(jsoncontent.__str__)))
        if redisresult:
            print '从redids取的数据'
            response_data['result'] = '1'

            response_data['ports'] = redisresult['ports']
            response_data['portslength'] = redisresult['portslength']
            response_data['resultsize'] = redisresult['resultsize']
        else:
            ports, portcount, portpagecount = getattr(mapcontrol, 'mapshow', 'mapshow')(**jsoncontent)
            redisdic = {}
            redisdic['ports'] = ports
            redisdic['portslength'] = portcount
            redisdic['resultsize'] = portpagecount
            redistool.set(webtool.md5(str(jsoncontent.__str__)), redisdic)
            response_data['result'] = '1'
            response_data['ports'] = ports
            response_data['portslength'] = portcount
            response_data['resultsize'] = portpagecount

        response_data['username'] = username

    try:

        return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict),
                            content_type="application/json")
    except Exception, e:
        print e
        return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict, encoding='latin-1'),
                            content_type="application/json")


def detailmapview(request):


    username = request.COOKIES.get('username', '')
    ip = request.GET.get('ip', '')
    return render_to_response('fontsearchview/detailmapview.html', {'data': '', 'username': username,'ip':ip})
def map(request):


    username = request.COOKIES.get('username', '')
    latitude=request.GET.get('latitude',0)
    longitude=request.GET.get('longitude',0)
    return render_to_response('fontsearchview/map.html', {'data': '', 'username': username,'latitude':latitude,'longitude':longitude})
def ipinfo(request):
    ip=request.POST.get('ip','127.0.0.1')
    response_data={}
    response_data['result'] = '0'
    data={}
    data['ip']=ip

    try:
        import sys
        sys.path.append("..")
        from elasticsearchmanage import ipestool
        ips, ipcount, ippagecount = ipestool.ipsearch(dic=data)
        response_data['result'] = '1'

        response_data['ips'] = ips
        response_data['iplength'] = ipcount
        response_data['ippagecount'] = ippagecount


    except:
        pass
    try:
        return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict),
                        content_type="application/json")
    except Exception,e:

        print e
        return HttpResponse(json.dumps(response_data, skipkeys=True, default=webtool.object2dict, encoding='latin-1'),
                            content_type="application/json")

