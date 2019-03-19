import requests,re,os,sys,json,copy
from bs4 import BeautifulSoup
log=open("ngaVoteLog.txt","w")
#https://bbs.nga.cn/read.php?tid=16683315&_ff=564
#https://bbs.nga.cn/read.php?tid=16683351&_ff=564
#https://bbs.nga.cn/read.php?tid=16683389&_ff=564
#https://bbs.nga.cn/read.php?tid=16683435&_ff=564

users_id=[]#投票用户id
comment_raw=[]#楼层投票原生字符串
comment_ind=[]#楼层索引
kansens=[]#参赛舰舰名
votes=[]#参赛舰获票数

floor=0
try:
  with open("Result.json","r") as f:
    firstline=json.loads(f.readline())
    if "kansens" in firstline and "votes" in firstline:
      if len(firstline["kansens"])==len(firstline["votes"]):
        print("发现上次未完成的记录，是否重新载入？")
        askconf=input("输入y以确认，否则请按回车：")
        if askconf!="y":
          raise NameError("Reload Denied")
        kansens=firstline["kansens"]
        votes=firstline["votes"]
        comment_process=[]
        for i in f:
          js=json.loads(i)
          comment_ind.append(js["floor"])
          users_id.append(js["user"])
          comment_process.append(js["comment"])
except:
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
  try:
    print("请输入投票截止日期，留空则视为禁用投票截止计算")
    print("格式:年月日时分")
    print("例子:201903182030")
    reply_time_before=int(input(">>>"))#投票日期
  except:
    reply_time_before=0
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
  hds["Cookie"]=input("(不懂就先敲回车)Cookie:")
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
    global reply_time_before
    sp=BeautifulSoup(req.content,"html.parser")
    reply_list=sp.find_all("table",attrs={"class":"forumbox postbox"})
    if if_first==True:
      host=reply_list.pop(0)#防止楼主进记录,生成参赛者名单

      participants=re.findall(re.compile("jpg\\[/img\\]<br/><br/>(.*?)<br/><br/>\\[/quote\\].*?"),str(host))[0]

      global kansens
      #print(participants)
      kansens=participants.split("<br/>")
      global votes
      votes=[0 for ii in range(len(kansens))]
      for ii in range(kansens.count('')):
        tag=kansens.index('')
        del kansens[tag]
        del votes[tag]
      print(kansens)
      #print(votes)
      os.system("pause")
    #retrytime=20
    for i in reply_list:
      #print(str(i))
      flr=int(re.findall(re.compile('''postcontainer(.*?)["'].*?'''),str(i))[0])#'
      if reply_time_before>201903080240 and not if_first:
        rpt=re.findall(re.compile('''title=['"]reply time["']>(.*?)</span></div>.*?'''),str(i))[0]
        rpt=rpt.replace("-","")
        rpt=rpt.replace(" ","")
        rpt=rpt.replace(":","")
        #print(rpt)
        if int(rpt)>reply_time_before:
          print("检测到截止日期已过")
          raise NameError("Capture Completed")
      if flr<=floor:
        # if retrytime>0:
        #   retrytime-=1
        #   continue
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

  comment_ind=[int(i+1) for i in range(len(comment_raw))]


  voted_uid=[]
  print("投票有效性验证中……")

  ifchk=input("是否检测投票用户注册时间？是请输入y：")
  if ifchk=="y":
    p=1
    for i in users_id:#根据规则进行一些处理
      check_reg=ses.get("https://bbs.nga.cn/nuke.php?__lib=ucp&__act=get&lite=js&uid=%s"%i,headers=hds).content.decode("gbk","replace")
      try:
       regdate=int(re.findall(re.compile('''"regdate":(.*?),.*?'''),check_reg)[0])
      except IndexError:
        print("找不到注册时间，用户%s,内容"%i,check_reg)
        p+=1
        continue
      #print(p/len(users_id)*100,"%",sep='')
      if p*100//len(users_id)%10==0:
        print(p/len(users_id)*100,"%",sep='')
      p+=1
      if regdate>1551369600:
        print("发现用户%s注册时间晚于2019年3月1日零点，抹去该用户投票"%i)
        log.write("发现用户%s注册时间晚于2019年3月1日零点，抹去该用户投票\n"%i)
        while i in users_id:
          pos=users_id.index(i)
          del users_id[pos]
          del comment_raw[pos]
          del comment_ind[pos]
        continue
      elif i not in voted_uid:
        voted_uid.append(i)
      else:
        print("发现用户%s发表了多个回复，只保留第一个"%i)
        log.write("发现用户%s发表了多个回复，只保留第一个\n"%i)
        while users_id.count(i)>1:
          pos=users_id.index(i,users_id.index(i)+1)
          del users_id[pos]
          del comment_raw[pos]
          del comment_ind[pos]

  #try:
  with open("ngaResult.json","w") as fr:#保存用户投票记录到文件
    for j in range(len(users_id)):
      fr.writelines(json.dumps({users_id[j]:comment_raw[j]})+"\n")
  print("投票页面信息获取已经完成，切换到本地数据操作模式，输入h可查看帮助")
  comment_process=copy.deepcopy(comment_raw)



trfrom=[]
trto=[]
trrefrom=[]
trreto=[]

igfrom=[]
igrefrom=[]

def swi(a,b):
  return b,a

def chkdic(i):
  global trfrom
  global trrefrom
  global trto
  global trreto
  global igfrom
  global igrefrom
  global kansens
  global votes
  global cur_vote
  cur_vote=[0 for ii in range(len(kansens))]
  
  
  for ii in range(len(igrefrom)):
    i=re.sub(igrefrom[ii],'',i)
  for ii in range(len(igfrom)):
    i=i.replace(igfrom[ii],'')
  
  
  for ii in range(len(trfrom)):
    i=i.replace(trfrom[ii],trto[ii])
    for ii in range(len(kansens)):
      if i.find(kansens[ii])!=-1:
        i=i.replace(kansens[ii],'')
        cur_vote[ii]=1
    
  for ii in range(len(trrefrom)):
    i=re.sub(trrefrom[ii],trreto[ii],i)
    for ii in range(len(kansens)):
      if i.find(kansens[ii])!=-1:
        i=i.replace(kansens[ii],'')
        cur_vote[ii]=1

  return i

while True:
  cmd=input(">>>")
  if cmd=="h":
    print("可用命令：addig addtr ld auto show ato score manu pass save")
    print("输入命令以查看具体用法")
    
#############################################save
  elif cmd[:4]=="save":
    print("此操作将会把剩余未处理的记录保存为文件，输入q以离开")
    askconf=input("按下回车以继续：")
    if askconf=="q":
      continue
    else:
      with open("给人看的结果.txt","w") as fwh:
        fwh.write("舰娘当前计分：\n")
        for i in range(len(kansens)):
          fwh.write(kansens[i]+":"+str(votes[i])+"\n")
        fwh.write("============================================\n")
        fwh.write("楼层\t用户id\t评论内容\n")
        with open("Result.json","w") as fw:
          fw.write(json.dumps({"kansens":kansens,"votes":votes})+"\n")
          for i in range(len(comment_process)):
            fw.write(json.dumps({"floor":comment_ind[i],"user":users_id[i],"comment":comment_process[i]})+"\n")
            fwh.write(str(comment_ind[i])+"\t"+str(users_id[i])+"\t"+comment_process[i]+"\n")
      print("记录已经保存到当前目录")
      print("Result.json可用于重载进度")
      print("重载方法为重新启动本脚本")
      print("并确保当前工作目录下存在Result.json")
      
#############################################addig
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

#############################################addtr
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

################################################ld
  elif cmd[:2]=="ld":
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
      a1=0
      a2=1
      while a1<len(igfrom)-1:#去重
        a2=a1+1
        while a2<len(igfrom):
          if igfrom[a1]==igfrom[a2]:
            igfrom.pop(a2)
          else:
            a2+=1
        a1+=1
      a1=0
      a2=1
      while a1<len(trrefrom)-1:
        a2=a1+1
        while a2<len(trrefrom):
          if trrefrom[a1]==trrefrom[a2]:
            trrefrom.pop(a2)
            trreto.pop(a2)
          else:
            a2+=1
        a1+=1
      a1=0
      a2=1
      while a1<len(trfrom)-1:
        a2=a1+1
        while a2<len(trfrom):
          if trfrom[a1]==trfrom[a2]:
            trfrom.pop(a2)
            trto.pop(a2)
          else:
            a2+=1
        a1+=1
      a1=0
      a2=1
      while a1<len(igrefrom)-1:
        a2=a1+1
        while a2<len(igrefrom):
          if igrefrom[a1]==igrefrom[a2]:
            igrefrom.pop(a2)
          else:
            a2+=1
        a1+=1
        
      a1=len(igfrom)-1
      a2=a1-1
      doneli=[False for i in igfrom]
      #对列表进行子字符串处理，利用冒泡排序
      while a1>0:
        a2=a1-1
        while doneli[a1]:
            a1-=1
        while a2>0:
          try:

            tmp=igfrom[a1].index(igfrom[a2])

            igfrom[a1],igfrom[a2]=swi(igfrom[a1],igfrom[a2])
            a1=a2
            
          except ValueError:
            pass
          a2-=1
        doneli[a1]=True
        a1-=1
      with open("ngaIgnore_dict.txt","w") as fa:
        for i in igfrom:
          fa.write(json.dumps({"type":"n","from":i})+"\n")
      with open("ngaIgnore_dict.txt","a") as fa:      
        for i in igrefrom:
          fa.write(json.dumps({"type":"re","from":i})+"\n")
      print(trrefrom)
      print(trreto)
      print(trfrom)
      print(trto)
      print(igrefrom)
      print(igfrom)

##############################################pass
  elif cmd[:4]=="pass":
    i=comment_process[0]
    tpi=i
    i=chkdic(i)
    while True:		
      print(tpi,"的处理结果：")
      for jj in range(len(kansens)):
        print(jj,kansens[jj],cur_vote[jj])
    
      askconf=input("输入q以离开,或输入舰娘名或对应下标以修改此票，否则回车将此票计入:")
      if askconf=="q":
        break
      try:
        tag=kansens.index(askconf)
        cur_vote[tag]=cur_vote[tag]^1
      except:
        pass
      if askconf.isdigit():
        cur_vote[int(askconf)]=cur_vote[int(askconf)]^1
      elif askconf=='':
        if cur_vote.count(1)>3:
          print("警告：当前投票对象大于3个")
        votes=[votes[ii]+cur_vote[ii] for ii in range(len(votes))]
        log.write("手动计票\t 楼层：%d\t字符：%s\n"%(comment_ind[0],comment_process[0]))
        for ii in range(len(cur_vote)):
          log.write(str(kansens[ii])+":"+str(cur_vote[ii])+"\n")
        comment_process.pop(0)
        users_id.pop(0)
        comment_ind.pop(0)
        break
      else:
        print("无法理解的指令")

##############################################manu
  elif cmd[:4]=="manu":
    print("此操作是输出处理第一个记录结果，需先运行ld和show")
    cmdchr=input("输入q可返回，否则按回车继续：")
    if cmdchr=="q":
      continue
    else:
      i=comment_process[0]
      tpi=i
      i=chkdic(i)
      print(i)
      
##############################################auto
  elif cmd[:4]=="auto":
    print("此操作是自动处理投票记录，需先运行ld")
    cmdchr=input("输入q可返回，否则按回车继续：")
    if cmdchr=="q":
      continue
    else:
      inte=0
      while inte < len(comment_process):
        tpi=comment_process[inte]
        i=chkdic(comment_process[inte])
        if cur_vote.count(1)>3:
          print("投票对象大于3个，%s作废"%tpi)
          log.write("投票对象大于3个，%s作废\n"%tpi)
          comment_process.pop(inte)
          comment_ind.pop(inte)
          users_id.pop(inte)
          continue
        elif i=='':
          print("已处理\t%s"%tpi)
          log.write("已处理\t%s:\n"%tpi)
          for ii in range(len(cur_vote)):
            log.write(str(kansens[ii])+":"+str(cur_vote[ii])+"\n")
          votes=[votes[ii]+cur_vote[ii] for ii in range(len(votes))]
          comment_process.pop(inte)
          comment_ind.pop(inte)
          users_id.pop(inte)
        else:
          inte+=1
          
###############################################ato
  elif cmd[:3]=="ato":
    print("剩余%d条记录因无法完美匹配无法自动处理"%len(comment_process))
    
##############################################show
  elif cmd[:4]=="show":
    try:
      showargv=int(cmd[5:])
      if showargv>len(comment_process):
        print("剩余记录数：%d；参数过大"%len(comment_process))
        continue
      for i in range(showargv):
        print(comment_process[i])
      continue
    except:
      pass
    #print("show 欲显示的记录数；示例：")
    #print("show 23")
    print("默认打印最近5条无法自动处理的记录：")
    for i in range(5):
      print(comment_process[i])
      
#############################################score
  elif cmd[:5]=="score":
    print("目前舰娘得票数：")
    for i in range(len(kansens)):
      print(kansens[i],"\t",votes[i])
  else:
    print("无法理解的命令：%s"%cmd)
log.close()
