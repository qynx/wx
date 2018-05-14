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
import json
import requests

sys.path.append('..')
from wxsys import getinfo

replyxml='''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
        </xml>
        '''

imgxml='''
<xml>
<ToUserName><![CDATA[{}]]></ToUserName>
<FromUserName><![CDATA[{}]]></FromUserName>
<CreateTime>{}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image><MediaId><![CDATA[{}]]></MediaId></Image>
</xml>
'''

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
        
        if xmldata.find('MsgType').text=='text':
            conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
            cursor=conn.cursor()
            sql='select * from state where openid="%s"'%(touser)
            cursor.execute(sql)
            results=cursor.fetchone()
            conn.commit()
        
            if not results:
                sql='insert into state values("%s","%s")'%(touser,'0')
                cursor.execute(sql)
                conn.commit()
                conn.close()

                reply=testreply(touser,xmldata.find('ToUserName').text,'欢迎')
                return HttpResponse(reply,content_type="applcation/xml")

            elif results[1]=='tobebind':
                send=bindself(xmldata)
                return HttpResponse(send,content_type="application/xml")

        elif xmldata.find('MsgType').text=='event':  
            if xmldata.find('Event').text=='click'.upper():  
                if xmldata.find('EventKey').text=='bind':

                    #request.session['touser']='tobebind'
                    touser=xmldata.find('FromUserName').text
                    fromuser=xmldata.find('ToUserName').text

                    #用户准备进入绑定状态，需要修改数据库状态 如果用户第一次进入，数据库没有相应记录需要先插入记录
                    conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
                    cursor=conn.cursor()
                    sql='select * from state where openid="%s"'%(touser)                    
                    cursor.execute(sql)

                    if cursor.fetchone()==None:

                        sql='insert into state values("%s","%s")'%(touser,'tobebind')
                        cursor.execute(sql)
                        #print('插入')
                    
                    else:
                        sql='update state set states ="tobebind" where openid="%s"'%(touser)
                        cursor.execute(sql)

                    conn.commit()
                    conn.close()
                    
                    reply=makebindreply(touser,fromuser)
                    
                    #print(reply)
                    
                    return HttpResponse(reply,content_type="application/xml")
                
                elif xmldata.find('EventKey').text=='grade_get':

                    user=xmldata.find('FromUserName').text  #用户id
                    platform=xmldata.find('ToUserName').text #平台

                    reply = gradeGet(user,platform)
                    print(reply)
                    return HttpResponse(reply,content_type="application/xml")

    touser=xmldata.find('FromUserName').text
    fromuser=xmldata.find('ToUserName').text
    reply=testreply(touser,fromuser)
    #print(reply)
    return HttpResponse(reply,content_type="application/xml")

#grade get
def gradeGet(user,platform):

    '''
    user openid
    platform plat
    获取成绩
    '''
    
    #查询是否绑定
    conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
    cursor=conn.cursor()
    sql='select * from user where openid = "%s"'%(user)
    cursor.execute(sql)

    userrecord=cursor.fetchone()

    if userrecord==None:
        return replyxml.format(user,platform,int(time.time()),"还未绑定 , 绑定后再来查询吧！")


    instance=Login(userrecord[0],userrecord[1])

    if instance.login()==0:

        response=instance.getGrade() #return response content of Image object
       
        g=getinfo.Get()
        access=g.loadaccesstoken()
        print(access)
        imgurl='https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type=image'.format(access)

        filename=userrecord[0]+'.png'
        files={'attachement_file':(filename,response,'image/png',{})}
        r=requests.post(imgurl,files=files)
        print(r.text)
        jsondata=json.loads(r.text)

        media_id=jsondata['media_id']
        print(media_id)
        return imgxml.format(user,platform,int(time.time()),media_id)
    else:
        return replyxml.format(user,platform.int(time.time()),"获取失败，后台抢修中。。。")


    

#bind
def bindself(xmldata):
    #print("bindself ...")
    content=xmldata.find('Content').text
    content=content.split('\n')
    touser=xmldata.find('FromUserName').text
    fromuser=xmldata.find('ToUserName').text
   
    try:
        usernumber=content[0]
        password=content[1]
    except Exception as e:
        conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
        cursor=conn.cursor()
        sql='update state set states = 0 where openid ="%s"'%(touser)
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return errorreply(touser,fromuser,"输入格式有错，账号密码要换行。。\n点击绑定 重新绑定")

    touser=xmldata.find('FromUserName').text
    fromuser=xmldata.find('ToUserName').text

    instance=Login(usernumber,password)

    result=instance.bind()
    #print(result)
    conn=pymysql.connect(host='127.0.0.1',user='root',password='287830',database='wx',charset='utf8')
    cursor=conn.cursor()
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
        sql='update state set states = 0 where openid ="%s"'%(touser)
        cursor.execute(sql)
        conn.commit()
        conn.close()
        result_msg='绑定失败（账号或密码不正确）\n已自动退出预备登录状态\n重新绑定需要再次点击绑定'

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

def testreply(touser,fromuser,msg='新的功能有待完善'):
    xmlform='''
        <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
        </xml>
        '''
    return xmlform.format(touser,fromuser,int(time.time()),'新的功能有待完善')


def errorreply(touser,fromuser,errormsg):

    return replyxml.format(touser,fromuser,int(time.time()),errormsg)

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