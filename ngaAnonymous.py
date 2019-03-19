import requests,re,os,sys,json,copy
from bs4 import BeautifulSoup

lnk="https://bbs.nga.cn/read.php?tid=16626917"
ses=requests.session()
hds={
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Encoding":"gzip, deflate, br",
	"Accept-Language":"zh-CN,zh;q=0.9",
	"Cache-Control":"max-age=0",
	"Connection":"keep-alive",
	"Host":"bbs.nga.cn",
	"Referer":"https://bbs.nga.cn/read.php?tid=16626917&_ff=564",
	"Upgrade-Insecure-Requests":"1",
	"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}
ses.headers=hds
req=ses.get(lnk,headers=hds)
print(req)
print(req.headers)
print(ses.headers)
print(req.content.decode('gbk'))
print("\n"*6)
ckstr=re.findall(re.compile("lastvisit=.*?;"),req.headers["Set-Cookie"])[0]+" "
ckstr+=re.findall(re.compile("ngaPassportUid=.*?;"),req.headers["Set-Cookie"])[0]+" "
ckstr+=re.findall(re.compile("guestJs=.*?;"),req.content.decode('gbk','ignore'))[0][:-1]
ses.headers["Cookie"]=ckstr
req=ses.get(lnk+"&rand=233")
print(req)
print(ses.headers)
print(req.content.decode('gbk'))