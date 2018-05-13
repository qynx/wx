import requests
import pickle
import json
######################
#直接去调试接口提交吧#
######################
d={
  "button":[
      { 
        "name":"功能",
        "sub_button":[{
            "type":"click",
            "name":"绑定",
            "key":"bind",

           },{
            "type":"click",
            "name":"获取成绩",
            "key":"grade_get",

           }
        ]
      } 
          
    ]
} 
'''
d={
    "button": [
        {
            "name": "hyq", 
            "sub_button": [
                {
                    "type": "view", 
                    "name": "用户", 
                    "url": "xxx", 
                    "sub_button": [ ]
                }
            ]
        }
    ]
}
'''
f=open('cry.d','rb')
s=pickle.load(f)
f.close()
acc=json.loads(s.decode('utf-8'))
access=acc['access_token']
url='https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s'%(access)

response=requests.post(url,data=d)
print(response.text)
