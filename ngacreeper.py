import requests,re,os,sys,json,copy
from bs4 import BeautifulSoup
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.ssl_ import create_urllib3_context

users_id=[]#投票用户id
comment_raw=[]#楼层投票原生字符串
comment_ind=[]#楼层索引
kansens=[]#参赛舰舰名
votes=[]#参赛舰获票数
floor=0
try:
	ignore_dict=open("ngaIgnore_dict.txt","r")
	ignore_dict.close()
except:
	print("警告：尚未建立忽略字典，新建文件ngaIgnore_dict.txt于本目录")
	ignore_dict_temp=open("ngaIgnore_dict.txt","w")
	ignore_dict_temp.close()

try:
	translate_dict=open("ngaTranslate_dict.txt","r")
	translate_dict.close()
except:
	print("警告：尚未建立舰名转换字典，新建文件ngaTranslate_dict.txt于本目录")
	translate_dict_temp=open("ngaTranslate_dict.txt","w")
	translate_dict_temp.close()

lnk=input("请输入投票页链接，留空则用默认调试页")
if lnk=='':
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
hds["Cookie"]=input("(调试时可选)Cookie:")
if hds["Cookie"]=='':
	try:
		with open("ngack.txt","r") as fr:
			hds["Cookie"]=fr.read()
	except:
		hds["Cookie"]="taihe=993152ac186e4e29eb6da7a79cec80a7; taihe_session=7b139c8bcd002cd6282c34283639775e; UM_distinctid=16984dafa44593-0bba1cfe5cb1d9-43450521-1fa400-16984dafa45bb2; CNZZDATA30043604=cnzz_eid%3D70536919-1552710109-%26ntime%3D1552710109; CNZZDATA30039253=cnzz_eid%3D1371588293-1552710731-%26ntime%3D1552710731; Hm_lvt_5adc78329e14807f050ce131992ae69b=1552712137; ngaPassportOid=b9d996ccc7365574b2feef4c7a26f56c; ngacn0comUserInfo=CreeperUsers_voidf%09CreeperUsers_voidf%0939%0939%09%0910%090%090%090%090%09; ngacn0comUserInfoCheck=b728822895080f88d013d477be025f86; ngacn0comInfoCheckTime=1552712246; ngaPassportUid=60301802; ngaPassportUrlencodedUname=CreeperUsers_voidf; ngaPassportCid=X8opugmvmo688obredmpk49c7bkdbu8v97u78r2k; CNZZDATA1262314542=1985232761-1552708712-https%253A%252F%252Fbbs.nga.cn%252F%7C1552708712; lastvisit=1552712262; lastpath=/read.php?tid=16626917&_ff=564; bbsmisccookies=%7B%22uisetting%22%3A%7B0%3A%22e%22%2C1%3A1552712561%7D%2C%22insad_refreshid%22%3A%7B0%3A%22/9Iwlg9B2Wc975ynDjSzUTNs6BXXqTdX7Nsrxhase%22%2C1%3A1553316936%7D%2C%22pv_count_for_insad%22%3A%7B0%3A-45%2C1%3A1552755672%7D%2C%22insad_views%22%3A%7B0%3A1%2C1%3A1552755672%7D%7D; Hm_lpvt_5adc78329e14807f050ce131992ae69b=1552712262"
		with open("ngack.txt","w") as fw:
			fw.write(hds["Cookie"])
else:
	with open("ngack.txt","w") as fw:
		fw.write(hds["Cookie"])

#try:
req=ses.get(lnk,headers=hds)
#print(req.content.decode('gbk'))
def catch_page(req,if_first):
	global users_id
	global comment_raw
	global floor
	sp=BeautifulSoup(req.content,"html.parser")
	reply_list=sp.find_all("table",attrs={"class":"forumbox postbox"})
	if if_first==True:
		host=reply_list.pop(0)#防止楼主进记录,生成参赛者名单

		participants=re.findall(re.compile("jpg\\[/img\\]<br/><br/>(.*?)<br/><br/>\\[/quote\\].*?"),str(host))[0]

		global kansens
		kansens=participants.split("<br/>")
		global votes
		votes=[0 for ii in range(len(kansens))]
		print(kansens)
		print(votes)
		os.system("pause")
	#retrytime=20
	for i in reply_list:
		#print(str(i))
		flr=int(re.findall(re.compile('''postcontainer(.*?)["'].*?'''),str(i))[0])#'
		
		if flr<=floor:
			# if retrytime>0:
			#     retrytime-=1
			#     continue
			print("检测到楼层重复:%d,%d"%(flr,floor))
			raise NameError("Capture Completed")
		#retrytime=20
		floor=flr
		uid=re.findall(re.compile('''uid=(.*?)['"] id=.*?'''),str(i))
		com=re.findall(re.compile('''<span class=['"]postcontent ubbcode['"] id=['"]postcontent.+['"]>(.*?)</span>.*?'''),str(i))#'
		users_id.append(uid[0])
		comment_raw.append(com[0])
	print(len(users_id))
	print(len(comment_raw))
	#except:
		#pass

catch_page(req,True)
page_integer=2
while True:
	
	clnk=lnk+"&page=%d"%page_integer

	try:
		catch_page(ses.get(clnk,headers=hds),False)
	except:
		#print(ses.get(clnk,headers=hds))
		break
	page_integer+=1

comment_ind=[int(i) for i in range(len(comment_raw))]


voted_uid=[]
print("投票有效性验证中……")
p=1
# for i in users_id:#根据规则进行一些处理
# 	check_reg=ses.get("https://bbs.nga.cn/nuke.php?__lib=ucp&__act=get&lite=js&uid=%s"%i,headers=hds).content.decode("gbk")
# 	regdate=int(re.findall(re.compile('''"regdate":(.*?),.*?'''),check_reg)[0])
# 	print(p/len(users_id)*100,"%",sep='')
# 	p+=1
# 	if regdate>1551369600:
# 		print("发现用户%s注册时间晚于2019年3月1日零点，抹去该用户投票"%i)
# 		while i in users_id:
# 			pos=users_id.index(i)
# 			del users_id[pos]
# 			del comment_raw[pos]
# 			del comment_ind[pos]
# 		continue
# 	elif i not in voted_uid:
# 		voted_uid.append(i)
# 	else:
# 		print("发现用户%s发表了多个回复，只保留第一个"%i)
# 		while users_id.count(i)>1:
# 			pos=users_id.index(i,users_id.index(i)+1)
# 			del users_id[pos]
# 			del comment_raw[pos]
# 			del comment_ind[pos]

#try:
with open("ngaResult.json","w") as fr:#保存用户投票记录到文件
	for j in range(len(users_id)):
		fr.writelines(json.dumps({users_id[j]:comment_raw[j]})+"\n")
print("投票页面信息获取已经完成，切换到本地数据操作模式，输入h可查看帮助")
comment_process=copy.deepcopy(comment_raw)

log=open("ngaVoteLog.txt","w")

trfrom=[]
trto=[]
trrefrom=[]
trreto=[]

igfrom=[]
igrefrom=[]

while True:
	cmd=input(">>>")
	if cmd=="h":
		print("可用命令：addig addtr loaddic auto show ato score manu")
		print("输入命令以查看具体用法")
	elif cmd[:5]=="addig":
		try:
			cmdli=cmd[6:].split(" ")
			print(cmdli)
			if cmdli[0]=="re":
				with open("ngaIgnore_dict.txt","a") as fa:
					fa.write(json.dumps({"type":"re","from":cmdli[1]})+"\n")
			elif cmdli[0]=="n":
				with open("ngaIgnore_dict.txt","a") as fa:
					fa.write(json.dumps({"type":"n","from":cmdli[1]})+"\n")
			else:
				raise NameError("参数错误")
		except:
			print("命令执行失败")
			print("说明：\t添加指定的字符串到忽略字典中")
			print("\t如果回复楼层包含这些字符串则忽略")
			print("用法：\taddig 类型 字符串")
			print("\t其中类型支持re（正则表达式）和n（普通字串）")
			print("样例：\taddig re \\[s:.*?\\].*?")
			print("\taddig n [del]")
	elif cmd[:5]=="addtr":
		try:
			cmdli=cmd[6:].split(" ")
			print(cmdli)
			if cmdli[0]=="re":
				with open("ngaTranslate_dict.txt","a") as fa:
					fa.write(json.dumps({"type":"re","from":cmdli[1],"to":cmdli[2]})+"\n")
			elif cmdli[0]=="n":
				with open("ngaTranslate_dict.txt","a") as fa:
					fa.write(json.dumps({"type":"n","from":cmdli[1],"to":cmdli[2]})+"\n")
			else:
				raise NameError("参数错误")
		except:
			print("命令执行失败")
			print("说明：\t添加指定的字符串到转义字典中")
			print("\t如果回复楼层包含这些字符串则转换为相应舰娘名")
			print("用法：\taddtr 类型 别名字符串 原名字符串")
			print("\t其中类型支持re（正则表达式）和n（普通字串）")
			print("样例：\taddtr re 火.*?鲁.*? 火奴鲁鲁")
			print("\taddtr n 撸撸 火奴鲁鲁")
	elif cmd[:7]=="loaddic":
		cmdchr=input("此操作是重载字典，输入q可返回，否则按回车继续：")
		if cmdchr=="q":
			continue
		else:
			trfrom=[]
			trto=[]
			trrefrom=[]
			trreto=[]

			igfrom=[]
			igrefrom=[]

			with open("ngaTranslate_dict.txt","r") as fa:
				for i in fa:
					cur_dict=json.loads(i)
					if cur_dict["type"]=="re":
						trrefrom.append(cur_dict["from"])
						trreto.append(cur_dict["to"])
					elif cur_dict["type"]=="n":
						trfrom.append(cur_dict["from"])
						trto.append(cur_dict["to"])

			with open("ngaIgnore_dict.txt","r") as fa:
				for i in fa:
					cur_dict=json.loads(i)
					if cur_dict["type"]=="re":
						igrefrom.append(cur_dict["from"])
					elif cur_dict["type"]=="n":
						igfrom.append(cur_dict["from"])
			print(trrefrom)
			print(trreto)
			print(trfrom)
			print(trto)
			print(igrefrom)
			print(igfrom)
	elif cmd[:4]=="manu":
		print("此操作是输出处理第一个记录结果，需先运行loaddic和show")
		cmdchr=input("输入q可返回，否则按回车继续：")
		if cmdchr=="q":
			continue
		else:
			i=comment_process[0]
			tpi=i
			cur_vote=[0 for ii in range(len(kansens))]
			for ii in range(len(trfrom)):
				i=i.replace(trfrom[ii],trto[ii])
			for ii in range(len(trrefrom)):
				i=re.sub(trrefrom[ii],trreto[ii],i)
			for ii in range(len(igfrom)):
				i=i.replace(igfrom[ii],'')
			#print(igrefrom)
			for ii in range(len(igrefrom)):
				i=re.sub(igrefrom[ii],'',i)
				print(i)
			for ii in range(len(kansens)):
				if i.find(kansens[ii])!=-1:
					i=i.replace(kansens[ii],'')
					cur_vote[ii]=1
			print(i)
			
	elif cmd[:4]=="auto":
		print("此操作是自动处理投票记录，需先运行loaddic")
		cmdchr=input("输入q可返回，否则按回车继续：")
		if cmdchr=="q":
			continue
		else:
			inte=0
			while inte < len(comment_process):
				i=comment_process[inte]
				tpi=i
				cur_vote=[0 for ii in range(len(kansens))]
				for ii in range(len(trfrom)):
					i=i.replace(trfrom[ii],trto[ii])
				for ii in range(len(trrefrom)):
					i=re.sub(trrefrom[ii],trreto[ii],i)
				for ii in range(len(igfrom)):
					i=i.replace(igfrom[ii],'')
				for ii in range(len(igrefrom)):
					i=re.sub(igrefrom[ii],'',i)
					#print(i)
				for ii in range(len(kansens)):
					if i.find(kansens[ii])!=-1:
						i=i.replace(kansens[ii],'')
						cur_vote[ii]=1
						#print(cur_vote)
				if cur_vote.count(1)>3:
					print("投票对象大于3个，%s作废"%tpi)
					comment_process.pop(inte)
					continue
				elif i=='':
					print("%s的处理结果："%tpi)
					for jj in range(len(kansens)):
						print(kansens[jj],cur_vote[jj])
					votes=[votes[ii]+cur_vote[ii] for ii in range(len(votes))]
					comment_process.pop(inte)
				else:
					inte+=1
	elif cmd[:3]=="ato":
		print("剩余%d条记录因无法完美匹配无法自动处理"%len(comment_process))
	elif cmd[:4]=="show":
		print("正在打印最近5条无法自动处理的记录：")
		for i in range(5):
			print(comment_process[i])
	elif cmd[:5]=="score":
		print("目前舰娘得票数：")
		for i in range(len(kansens)):
			print(kansens[i],"\t",votes[i])
	else:
		print("无法理解的命令：%s"%cmd)
log.close()
