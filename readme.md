主要功能从 xx大学教务处查询成绩
并在微信展示

主要流程
1）用户从微信点击获取成绩
2）微信服务器转发xml到后台服务器
3）服务器解析xml文件进行相应操作
4）假设为获取成绩，后台根据用户OPENID获取用户
的对应教务系统的账号与密码（绑定时会验证）
5）拿到账号密码后（存于数据库中），开始登录
6）首先到登录表单，填入输入数据，获取验证码
7）处理验证码，识别，先判断识别结果是否为四位，或是否
有非法字符出现，若有，并不立即提交表单，再请求一次验证码
直至识别出验证码符合规范，提交表单
8）若返回结果失败，判断失败原因，若是密码错误，则提示用户
重新绑定，否则重新请求验证码，重新填写表单。
9）获取成功，根据微信的提交媒体文件的接口，提交获取的图片，获取图片的media——id
10）把返回的id提交给微信服务器，微信服务器返回对应图片给用户
11）流程结束

主要问题及解决方法

1）首先判断界面js加密数据方法，并用python实现（比较简单，主要是md5加密后，取一部分再次加密）
2）验证码降噪，在识别验证码之前必须降噪，这里注意从教务系统获取验证码之后并没有保存为本地，直接在内存中传到对应函数，  
file=np.asarray(bytearray(file),dtype='uint8') 其中file为从图片的二进制序列
。
二值化使用opencv的adaptiveThreshold. 之后进行线降噪和点降噪，线降噪检查四邻域，点降噪检查9邻域。
3）识别问题，直接把降噪后的图片提交tesseract处理，返回结果。
4）微信中，需要一个状态的维持（用户在点击绑定后，手动输入账号密码，这个输入要与普通输入区分开来，而且应该支持用户在输错一次后，不退出这个状态[接受用户输入账号密码的状态)]，这个通过在数据库为每一个用户加一个状态判断，0即不处于任何状态。

主要技术及框架,模块

1）Django 后台用Django搭建
2）OpencV 验证码降噪使用Opencv
3）tesseract 验证识别
4）requests

