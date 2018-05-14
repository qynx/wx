from .config import url_config as url
from .config import db_config as db
from .config import d_test_config as app_config
from datetime import datetime
import pickle
import json
import requests
import sqlite3
import logging

logging.basicConfig(filename='wx.log',level=logging.INFO)
####################
#从接口获取相关信息#
####################
class Get:
	'''
	从接口获取相关信息
	获取token getaccesstoken
	加载token loadaccesstoken

	'''
	def __init__(self):
		self.url=url
	
	def getaccesstoken(self):
		aurl=self.url['token_get']
		aurl=aurl.format(app_config['APPID'],app_config['APPSECRET'])
		response=requests.get(aurl)

		#conn=sqlite3.connect(db['db'])
		#cursor=conn.cursor()
		#sql='insert into %s values()'

		#f=open('cry.d','wb')
		#pickle.dump(response.content,f)
		#f.close()

		f=open('cry.txt','w')
		f.write(response.text)
		f.close()

		a=json.loads(response.text)
		#print(a)
		
		conn=sqlite3.connect(db['db'])
		cursor=conn.cursor()

		sql='insert into %s values("%s","%s")'%(db['accesstimetable'],a['access_token'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		#print(sql)
		cursor.execute(sql)

		#cursor.execute()
		conn.commit()
		conn.close()
		
	def loadaccesstoken(self):
		conn=sqlite3.connect(db['db'])
		#print(db['db'])
		sql='select * from %s  order by datetime desc'%(db['accesstimetable'])
		cursor=conn.cursor()
		cursor.execute(sql)
		fetch=cursor.fetchone()
		if not fetch:
			self.getaccesstoken()
			sql='select * from %s  order by datetime desc'%(db['accesstimetable'])
			cursor.execute(sql)
			fetch=cursor.fetchone()
			self.access=fetch[0]
			return self.access
			
		last_time=fetch[1]
		now=datetime.now()
		last_time=datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S")
		print(last_time)
		hour_cha=24*(now.day-last_time.day)+(now.hour-last_time.hour)
		print(hour_cha)
		if hour_cha>1:
			logging.info("%s: 刷新acesstoken\n"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
			
			self.getaccesstoken()

			sql='select * from %s  order by datetime desc'%(db['accesstimetable'])
			cursor.execute(sql)
			fetch=cursor.fetchone()
		conn.commit()
		conn.close()		
		#logging.info("%s: 刷新acesstoken\n"%(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))	
		#f=open('cry.d','rb')
		#s=pickle.load(f)
		#f.close()
		#acc=json.loads(s.decode('utf-8'))
		#print(fetch[0])
		self.access=fetch[0]
		return self.access

	def getOpenid(self):
		access=self.loadaccesstoken()
		#print(access)
		geturl=url['openid_get'].format(access)
		response=requests.get(geturl)
		print(response.text)
	

if __name__=='__main__':
	#g=Get(url)
	#g.getaccesstoken()
	g.loadaccesstoken()
	#g.getOpenid()
	#print(g.loadaccesstoken())
