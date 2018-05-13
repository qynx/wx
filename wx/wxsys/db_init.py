import sqlite3
import sys
from .config import db_config as db

conn=sqlite3.connect(db['db'])

cursor=conn.cursor()

initsql='''
drop table if exists %s;
drop table if exists %s;
'''%(db['usertable'],db['accesstimetable'])

try:
	mode=sys.argv[1]
	#print(mode)
	if mode=='0':

		cursor.executescript(initsql)
except Exception as e:
	pass

user_sql='''
		 create table {}(number varchar(20),password varchar(50),openid varchar(200) PRIMARY KEY)	
		 '''
time_sql='''
		create table {}(token varchar(200),datetime datetime)
		'''


user_sql=user_sql.format(db['usertable'])
time_sql=time_sql.format(db['accesstimetable'])

cursor.execute(user_sql)
cursor.execute(time_sql)

conn.commit()
conn.close()
