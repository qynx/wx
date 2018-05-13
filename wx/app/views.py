from django.shortcuts import render
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
# Create your views here.
import hashlib
import sys
import os
from PIL import Image
#Program_dir=os.path.dirname(os.path.dirnme(os.path.abspath(__file__)))
#search_path=os.path.join(Program_dir,'sys')
#sys.path.insert(0,search_path)
from .parses import Login
from io import BytesIO
import xml.etree.ElementTree as ET
import time
import pymysql
@csrf_exempt
def weixin_main(request):
    if request.method == "GET":
        #接收微信服务器get请求发过来的参数
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        #服务器配置中的token
        token = 'nicaibudaoaaaa'
        #把参数放到list中排序后合成一个字符串，再用sha1加密得到新的字符串与微信发来的signature对比，如果相同就返回echostr给服务器，校验通过
        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        hashstr = ''.join([s for s in hashlist])
        hashstr = hashlib.sha1(hashstr.encode('utf-8')).hexdigest()
        if hashstr == signature:
          return HttpResponse(echostr)
        else:
          return HttpResponse("field")
    else:
        webdata=request.body
        xmldata=ET.fromstring(webdata)
        #print(webdata)
        touser=xmldata.find('FromUserName').text
        #print(request.session.get('touser',None))
        
        conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
        cursor=conn.cursor()
        sql='select * from state where openid="%s"'%(touser)
        cursor.execute(sql)
        results=cursor.fetchone()
        conn.commit()
        conn.close()
        if results[1]=='tobebind':
            send=bindself(xmldata)
            return HttpResponse(send,content_type="application/xml")

        if xmldata.find('MsgType').text=='event':
            if xmldata.find('Event').text=='click'.upper():
                if xmldata.find('EventKey').text=='bind':

                    request.session['touser']='tobebind'
                    touser=xmldata.find('FromUserName').text
                    fromuser=xmldata.find('ToUserName').text


                    conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
                    cursor=conn.cursor()
                    sql='select * from state where openid="%s"'%(touser)                    
                    cursor.execute(sql)
                    if cursor.fetchone()==None:

                        sql='insert into state values("%s","%s")'%(touser,'tobebind')
                        cursor.execute(sql)
                        print('插入')
                    else:
                        sql='update state set states ="tobebind" where openid="%s"'%(touser)
                        cursor.execute(sql)

                    conn.commit()
                    conn.close()
                    reply=makebindreply(touser,fromuser)
                    print(reply)
                    return HttpResponse(reply,content_type="application/xml")
    touser=xmldata.find('FromUserName').text
    fromuser=xmldata.find('ToUserName').text
    reply=testreply(touser,fromuser)
    #print(reply)
    return HttpResponse(reply,content_type="application/xml")

#bind
def bindself(xmldata):
    print("bindself ...")
    content=xmldata.find('Content').text
    content=content.split('\n')
    usernumber=content[0]
    password=content[1]
    touser=xmldata.find('FromUserName').text
    fromuser=xmldata.find('ToUserName').text
    instance=Login(usernumber,password)

    result=instance.bind()
    print(result)
    if result==0:
        
       
        conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
        cursor=conn.cursor()
        sql='insert into user(number,password,openid) values("%s","%s","%s")'%(usernumber,password,xmldata.find('FromUserName').text)
        cursor.execute(sql)
        sql='update state set states = 0 where openid ="%s"'%(touser)
        cursor.execute(sql)
        conn.commit()
        conn.close()

        result_msg='绑定成功'
    else:
        reuslt_msg='绑定失败（账号或密码不正确）'

    xmlform='''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
        </xml>
        '''
    return xmlform.format(touser,fromuser,int(time.time()),result_msg)
def testreply(touser,fromuser):
    xmlform='''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
        </xml>
        '''
    return xmlform.format(touser,fromuser,int(time.time()),'GG了')

def makebindreply(touser,fromuser):
    xmlform='''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
        </xml>
        '''
    return xmlform.format(touser,fromuser,int(time.time()),'输入帐号和密码,格式如下：\n2015213213312\ndsada\n')


def test(request):
	return HttpResponse("this is a test ")

def get(request):
	number=request.GET['number']
	password=request.GET['password']

	instance=Login(number,password)

	instance.login()
	content=instance.getGrade()
	#img=Image.open(content)
	#f=BytesIO()
	#img.save(f,'png')
	#l=f.getValue()
	#f.close()
	return HttpResponse(content,content_type="image/png")
def submit(request):
	pass

def login(request):
    if request.method=='GET':
        html='''
        <form method="post" action="/wx/login">
        
        <input type="text" id="number" name="number"  placeholder="输入账号"/>
        <input type="password" id="password" name="password" placeholder="输入密码"/>       
        <input type="submit" id="sub" name="sub" value="提交"/>
        </form>
        '''
        return HttpResponse(html)

    elif request.method=='POST':
        user=request.POST['number']
        password=request.POST['password']
        print(user+password)
        return HttpResponse("<h1>提交成功</h1>")

#'2014510251626','54321'