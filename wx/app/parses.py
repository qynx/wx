import hashlib
import requests
from requests.adapters import HTTPAdapter
from PIL import Image
from io import BytesIO
import re
from cvtest import clean_bg
import numpy as np
import logging
from datetime import datetime 
import pickle

logging.basicConfig(filename='logger.log',level=logging.INFO)
config={
		'yzmurl':'http://58.20.34.197:10089/jwweb/sys/ValidateCode.aspx',
		'loginurl':'http://58.20.34.197:10089/jwweb/_data/login_new.aspx',
		'gradeurl':'http://58.20.34.197:10089/jwweb/xscj/Stu_MyScore_rpt.aspx',
		'gradeurl_prefix':'http://58.20.34.197:10089/jwweb/xscj/',
	}

class Login:
	def __init__(self,number,password,yzm='1234',cofig=config):
		self.number=number
		self.password=password
		self.form={
			"__VIEWSTATE":	"",
			"dsdsdsdsdxcxdfgfg":	"",
			"fgfggfdgtyuuyyuuckjg":	"",
			"pcInfo":	"Mozilla/5.0+(Windows+NT+6.3;+WOW64;+rv:59.0)+Gecko/20100101+Firefox/59.0Windows+NT+6.3;+WOW645.0+(Windows)+SN:NULL",
			"Sel_Type":	"STU",
			"txt_asmcdefsddsd":self.number,
			"txt_pewerwedsdfsdff":"",	
			"txt_sdertfgsadscxcadsads":"",
			"typeName":"%D1%A7%C9%FA",
		}
		self.headers={
			"Host":	"58.20.34.197:10089",
			"Referer":"http://58.20.34.197:10089/jwweb/_data/login_new.aspx",
			"User-Agent":	"Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/59.0".encode('utf-8'),
		}
		self.config=config
		self.s = requests.session()
		self.s.mount('http://', HTTPAdapter(max_retries = 3))
		self.s.mount('https://', HTTPAdapter(max_retries = 3))
		self.yzm=yzm

		self.yc=0
		self.sc=0
		#init()
	

	#encrypt the password
	def chkpwd(self):
		if self.password=='':
			Warning.warn('密码为空')
		if self.number=='':
			Warning.warn('学号为空')

		temp=self.number+hashlib.md5(self.password.encode('utf-8')).hexdigest()[0:30].upper()+'13806'

		result=hashlib.md5(temp.encode('utf-8')).hexdigest()[0:30].upper()
		self.dsdsdsdsdxcxdfgfg=result

	#encrypt the check code
	def chkyzm(self):
		if self.chkyzm=='1234':
			Warning.warn('随机验证码')
			#self.fgfggfdgtyuuyyuuckjg=self.yzm.upper()
		#print(self.yzm)
		temp=hashlib.md5(self.yzm.upper().encode('utf-8')).hexdigest()[0:30].upper()+'13806'
		result=hashlib.md5(temp.encode('utf-8')).hexdigest()[0:30].upper()
		#print(result)
		self.fgfggfdgtyuuyyuuckjg=result


	#load the check code
	def loadyzm(self):
		self.yc+=1
		headers={
			"Referer":	"http://58.20.34.197:10089/jwweb/_data/login_new.aspx",
			"User-Agent":	"Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/59.0".encode('utf-8'),
		}
		url=self.config['yzmurl']
		#print("loading the check image...")
		#print(self.s.cookies)
		response=self.s.get(url,headers=headers).content
		#f=BytesIO()
		#f.write(response)
		
		#img=Image.open(f)
		#img.show()
		#yzminput=input('输入你看到的验证码')
		#self.yzm=yzminput
		#img.save(f,'png')

		c=clean_bg(response)
		return c
	
	def autoloadyzm(self):
		while True:
			result=self.loadyzm()
			logging.info("%s : 获取验证码：%s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),result))
			#print(result)
			if result!=1:
				break
			logging.info("%s : 重新加载验证码 (并没有提交表单)"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
		#print(result)
		self.yzm=result

	
	def makeform(self):
		self.form['dsdsdsdsdxcxdfgfg']=self.dsdsdsdsdxcxdfgfg
		self.form['fgfggfdgtyuuyyuuckjg']=self.fgfggfdgtyuuyyuuckjg
		self.form['__VIEWSTATE']=self.viewstate

	def prepare_login(self):
		response=self.s.get(self.config['loginurl'],headers=self.headers).text
		#<input name="__VIEWSTATE" value="dDwyMTIyOTQxMzM0Ozs+DhUU++VKx3KfF1YAtbTrNVCUfYg=" type="hidden">
		#print(response)
		#print(self.s.cookies)
		pattern='name="__VIEWSTATE" value="(.*?)"'
		rem=re.compile(pattern,re.S)
		result=rem.findall(response)[0]
		#print(result)
		self.viewstate=result
		self.chkpwd()
		self.autoloadyzm()
		self.chkyzm()
		self.makeform()

	def cacheCookie(self):
		self.cookies = requests.utils.dict_from_cookiejar(self.s.cookies)
		self.cookies['number']=self.number
		#print(self.cookies)
		f=open(self.number+'.d','wb')
		pickle.dump(self.cookies,f)
		f.close()
		logging.info("%s : 缓存cookie: %s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))
	
	def loadCookie(self):
		f=open(self.number+'.d','rb')
		cookies=pickle.load(f)
		f.close()
		logging.info("%s : 加载cookie: %s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))	
		return cookies

	def login_cache(self):
		cookies=self.loadCookie()

		header=self.headers
		header['Referer']='http://58.20.34.197:10089/jwweb/xscj/Stu_MyScore.aspx'

		form={
		"btn_search":"%BC%EC%CB%F7",
		"sel_xn" :"2017",
		"sel_xq"	:"0",
		"SelXNXQ"	:"2",
		"SJ"	:"1",
		"zfx_flag":	"0",
		"zxf"	:"0"
		}
		header['Cookie']='ASP.NET_SessionId='+cookies['ASP.NET_SessionId']
		response=requests.post(self.config['gradeurl'],headers=header,data=form)
		pattern="src='(.*?)'"
		rec=re.findall(pattern,response.text)[0]
		#print(rec)
		url=self.config['gradeurl_prefix']+rec

		response=requests.get(url,headers=header).content
		f=BytesIO()
		f.write(response)
		logging.info("%s : 获取成绩(缓存cookie) %s \n----------------------"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))
		img=Image.open(f)
		img.show()
		f.close()
	
	def bind(self):
		self.prepare_login()
		while True:
			logging.info("%s : 绑定账号： %s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))
			response=self.s.post(self.config['loginurl'],data=self.form,headers=self.headers)
			if response.text.find('验证码错误')==-1:
				if response.text.find('帐号或密码不正确')>-1:
					return 1
				else:
					return 0
			else:
				self.autoloadyzm()
				self.chkyzm()
				self.makeform()


	def login(self):
		'''
		prepare for login
		return : 1 账号密码不正确
		return ：0 登录正常
		'''

		self.prepare_login()
		#print(self.form)
		while True:
			self.sc+=1
			logging.info("%s : 提交表单 验证码: %s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.yzm))
			response=self.s.post(self.config['loginurl'],data=self.form,headers=self.headers)
			if response.text.find('帐号或密码不正确')>-1:
				logging.info("%s : 账号密码不正确 %s"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))
				return 1
			if response.text.find('验证码错误')==-1:
				logging.info("%s : 登录成功"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
				#print(response.text)
				break

			else:
				logging.info("%s : 验证码错误"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
				self.autoloadyzm()
				self.chkyzm()
				self.makeform()
		self.cacheCookie()
		logging.info("%s : 本次登录共请求验证码 %s 次 提交表单 %s 次\n----------------------"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(self.yc),str(self.sc)))
		self.rc,self.sc=0,0
		return 0
		#print('登录成功',end='')		
		#print(self.s.cookies)

	def getGrade(self):
		header=self.headers
		header['Referer']='http://58.20.34.197:10089/jwweb/xscj/Stu_MyScore.aspx'

		form={
		"btn_search":"%BC%EC%CB%F7",
		"sel_xn" :"2017",
		"sel_xq"	:"0",
		"SelXNXQ"	:"2",
		"SJ"	:"1",
		"zfx_flag":	"0",
		"zxf"	:"0"
		}
		response=self.s.post(self.config['gradeurl'],headers=header,data=form)
		#print(response.text)
		pattern="src='(.*?)'"
		rec=re.findall(pattern,response.text)[0]
		#print(rec)
		url=self.config['gradeurl_prefix']+rec

		response=self.s.get(url,headers=header).content
		#f=BytesIO()
		#f.write(response)
		logging.info("%s : 获取成绩 %s \n----------------------"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.number))
		#img=Image.open(f)
		#img.show()
		#f.close()
		return response


if __name__=='__main__':
	
	instance=Login('2014510251626','54321','t4p4',config)
	'''
	instance.chkpwd()
	print(instance.dsdsdsdsdxcxdfgfg)
	instance.chkyzm()
	print(instance.fgfggfdgtyuuyyuuckjg)
	instance.loadyzm()
	'''
	if instance.login()==0:
	#instance.chkyzm()
		instance.getGrade()
	#instance.autoloadyzm()
	#instance.login_cache()

	#print(instance.bind())






xuehao='2014510250710'

