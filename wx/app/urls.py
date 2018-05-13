from django.conf.urls import url
from . import  views

urlpatterns=[
	url(r'^$',views.weixin_main,name='weixin_main'),
	url(r'^test/$',views.test,name='test'),
	url(r'^submit/$',views.submit,name='submit'),
	url(r'^get/$',views.get,name='get'),
]