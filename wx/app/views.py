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
        othercontent = autoreply(request)
        return HttpResponse(othercontent)

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