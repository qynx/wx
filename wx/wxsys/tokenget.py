import requests
from config import d_test_config as config
import pickle

url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(config['APPID'],config['APPSECRET'])

response=requests.get(url)

print(response.text)

f=open('cry.d','wb')
pickle.dump(response.content,f)
f.close()

f=open('cry.txt','w')
f.write(response.text)
f.close()




