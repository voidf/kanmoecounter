import requests,re,os,sys,json,copy,time
from bs4 import BeautifulSoup
#https://bbs.nga.cn/read.php?tid=16683315&_ff=564 小组A
#https://bbs.nga.cn/read.php?tid=16683351&_ff=564 小组B
#https://bbs.nga.cn/read.php?tid=16683389&_ff=564 小组C
#https://bbs.nga.cn/read.php?tid=16683435&_ff=564 小组D
class ngaC():
    def chkdic(self,i):
        self.cur_vote=[0 for ii in range(len(self.kansens))]
        
        for ii in range(len(self.igrefrom)):
            i=re.sub(self.igrefrom[ii],'',i)
        for ii in range(len(self.igfrom)):
            i=i.replace(self.igfrom[ii],'')
        
        for ii in range(len(self.trfrom)):
            i=i.replace(self.trfrom[ii],self.trto[ii])
            for iii in range(len(self.kansens)):
                if i.find(self.kansens[iii])!=-1:
                    i=i.replace(self.kansens[iii],'')
                    self.cur_vote[iii]=1
            
        for ii in range(len(self.trrefrom)):
            i=re.sub(self.trrefrom[ii],self.trreto[ii],i)
            for iii in range(len(self.kansens)):
                if i.find(self.kansens[iii])!=-1:
                    i=i.replace(self.kansens[iii],'')
                    self.cur_vote[iii]=1

        for ii in range(len(self.kansens)):
            if i .find(self.kansens[ii])!=-1:
                i=i.replace(self.kansens[ii],'')
                self.cur_vote[ii]=1
        return i


    def swi(a,b):
        return b,a
    def catch_page(self,req,if_first):

        sp=BeautifulSoup(req.content,"html.parser")
        reply_list=sp.find_all("table",attrs={"class":"forumbox postbox"})
        if if_first==True:
            host=reply_list.pop(0)#防止楼主进记录,生成参赛者名单

            participants=re.findall(re.compile("jpg\\[/img\\]<br/><br/>(.*?)<br/><br/>\\[/quote\\].*?"),str(host))[0]

            self.kansens=participants.split("<br/>")

            self.votes=[0 for ii in range(len(self.kansens))]
            self.cur_vote=[0 for ii in range(len(self.kansens))]

            for ii in range(self.kansens.count('')):
                tag=self.kansens.index('')
                del self.kansens[tag]
                del self.votes[tag]
            pstr=""
            for pi in self.kansens:
                pstr+=pi+" "
            print(pstr)

        for i in reply_list:
            flr=int(re.findall(re.compile('''postcontainer(.*?)["'].*?'''),str(i))[0])#'
            if self.reply_time_before>201903080240 and not if_first:
                rpt=re.findall(re.compile('''title=['"]reply time["']>(.*?)</span></div>.*?'''),str(i))[0]
                rpt=rpt.replace("-","")
                rpt=rpt.replace(" ","")
                rpt=rpt.replace(":","")

                if int(rpt)>self.reply_time_before:
                    print("检测到截止日期已过")
                    raise NameError("Capture Completed")
            if flr<=self.floor:
                print("检测到楼层重复:%d,%d"%(flr,self.floor))
                raise NameError("Capture Completed")

            self.floor=flr
            uid=re.findall(re.compile('''uid=(.*?)['"] id=.*?'''),str(i))
            com=re.findall(re.compile('''<span class=['"]postcontent ubbcode['"] id=['"]postcontent.+['"]>(.*?)</span>.*?'''),str(i))#'
            self.users_id.append(uid[0])
            self.comment_raw.append(com[0])
        print(str(len(self.users_id)))
        print(str(len(self.comment_raw)))

    def __init__(self):
        self.log=open("ngaVoteLog.txt","w")

        self.users_id=[]#投票用户id
        self.comment_raw=[]#楼层投票原生字符串
        self.comment_ind=[]#楼层索引
        self.kansens=[]#参赛舰舰名
        self.votes=[]#参赛舰获票数

        self.floor=0
        try:
            with open("Result.json","r") as f:
                firstline=json.loads(f.readline())
                if "kansens" in firstline and "votes" in firstline:
                    if len(firstline["kansens"])==len(firstline["votes"]):
                        print("发现上次未完成的记录，是否重新载入？")
                        askconf=input("输入y以确认，否则请按回车：")
                        if askconf!="y":
                            raise NameError("Reload Denied")
                        self.kansens=firstline["kansens"]
                        self.votes=firstline["votes"]
                        self.cur_vote=[0 for ii in range(len(self.kansens))]
                        self.comment_process=[]
                        for i in f:
                            js=json.loads(i)
                            self.comment_ind.append(js["floor"])
                            self.users_id.append(js["user"])
                            self.comment_process.append(js["comment"])
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
                self.reply_time_before=int(input(">>>"))#投票日期
            except:
                self.reply_time_before=0
            lnk=input("请输入投票页链接，留空则用默认调试页")
            if lnk=='':
                lnk="https://bbs.nga.cn/read.php?tid=16683389&_ff=564"
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
                    if ses.get(lnk,headers=hds).status_code==403:
                        raise NameError("Fake Cookie!Cookie过期啦或者不正确!")
                except:
                    req=ses.get(lnk,headers=hds)
                    for k,v in req.headers.items():
                        print(str(k)+": "+str(v) )
                    ckstr=re.findall(re.compile("lastvisit=.*?;"),req.headers["Set-Cookie"])[0]+" "
                    ckstr+=re.findall(re.compile("ngaPassportUid=.*?;"),req.headers["Set-Cookie"])[0]+" "
                    ckstr+=re.findall(re.compile("guestJs=.*?;"),req.content.decode('gbk','ignore'))[0][:-1]
                    hds["Cookie"]=ckstr
                    time.sleep(1)
                    lnk+="&rand=233"
                    #with open("ngack.txt","w") as fw:
                    #    fw.write(hds["Cookie"])
            else:
                if ses.get(lnk,headers=hds).status_code==200:
                    with open("ngack.txt","w") as fw:
                        fw.write(hds["Cookie"])
                else:
                    raise NameError("无效的Cookie,请重新确认或者回到上页使用游客Cookie")

            #try:
            req=ses.get(lnk,headers=hds)
            #print(req.content.decode('gbk'))
            
            self.catch_page(req,True)
            page_integer=2
            while True:
                
                clnk=lnk+"&page=%d"%page_integer

                try:
                    self.catch_page(ses.get(clnk,headers=hds),False)
                except:
                    #print(ses.get(clnk,headers=hds))
                    break
                page_integer+=1

            self.comment_ind=[int(i+1) for i in range(len(self.comment_raw))]


            voted_uid=[]
            print("投票有效性验证中……")

            ifchk=input("是否检测投票用户注册时间？是请输入y：")
            if ifchk=="y":
                p=1
                for i in self.users_id:#根据规则进行一些处理
                    check_reg=ses.get("https://bbs.nga.cn/nuke.php?__lib=ucp&__act=get&lite=js&uid=%s"%i,headers=hds).content.decode("gbk","replace")
                    try:
                        regdate=int(re.findall(re.compile('''"regdate":(.*?),.*?'''),check_reg)[0])
                    except IndexError:
                        print("找不到注册时间，用户%s,内容:%s"%(i,check_reg))
                        if int(i)==-1:
                            print("uid为-1，判断为匿名用户")
                        p+=1
                        continue
                    #print(p/len(users_id)*100,"%",sep='')
                    if p*100//len(self.users_id)%10==0:
                        print(str(p/len(self.users_id)*100)+"%")
                    p+=1
                    if regdate>1551369600:
                        print("发现用户%s注册时间晚于2019年3月1日零点，抹去该用户投票"%i)
                        self.log.write("发现用户%s注册时间晚于2019年3月1日零点，抹去该用户投票\n"%i)
                        while i in self.users_id:
                            pos=self.users_id.index(i)
                            del self.users_id[pos]
                            del self.comment_raw[pos]
                            del self.comment_ind[pos]
                        continue
                    elif i not in voted_uid:
                        voted_uid.append(i)
                    else:
                        print("发现用户%s发表了多个回复，只保留第一个"%i)
                        self.log.write("发现用户%s发表了多个回复，只保留第一个\n"%i)
                        while self.users_id.count(i)>1:
                            pos=self.users_id.index(i,self.users_id.index(i)+1)
                            del self.users_id[pos]
                            del self.comment_raw[pos]
                            del self.comment_ind[pos]

    #try:
            with open("ngaResult.json","w") as fr:#保存用户投票记录到文件
                for j in range(len(self.users_id)):
                    fr.writelines(json.dumps({self.users_id[j]:self.comment_raw[j]})+"\n")
            print("投票页面信息获取已经完成，切换到本地数据操作模式，输入h可查看帮助")
            self.comment_process=copy.deepcopy(self.comment_raw)



        self.trfrom=[]
        self.trto=[]
        self.trrefrom=[]
        self.trreto=[]

        self.igfrom=[]
        self.igrefrom=[]





        while True:
            self.log.flush()
            cmd=input(">>>")
            if cmd=="h":
                print("可用命令：addig addtr ld auto show ato score manu pass save brute dig dtr q")
                print("输入命令以查看具体用法")
            elif cmd=="q":
                confirm=input("退出，确认？(Y/n)")
                if confirm=="n":
                    continue
                else:
                    break
        ############################################brute
            elif cmd[:5]=="brute":
                print("这里是暴力计数，将剩余评论一次计完，忽略未完全匹配的结果。")
                print("不会影响主计票的进度，仅用于估计和参考。")
                brutevote=copy.deepcopy(self.votes)
                for i in self.comment_process:
                    t=self.chkdic(i)

                    if self.cur_vote.count(1)>3:
                        print("%s 投票对象大于3个，作废"%i)
                    else:
                        brutevote=[brutevote[ii]+self.cur_vote[ii] for ii in range(len(brutevote))]
                print("暴力计票结果：")
                for i in range(len(self.kansens)):
                    print(self.kansens[i]+"\t"+" "+str(brutevote[i]))
        ###############################################dd
            elif cmd[:3]=="dig":
                try:
                    cmdli=cmd[4:].split(" ")
                    if cmdli[0]=="n" and cmdli[1].isdigit():
                        try:
                            del igfrom[int(cmdli[1])]
                        except IndexError:
                            print("数组越界")
                        except:
                            print("格式错误")
                    elif cmdli[0]=="re" and cmdli[1].isdigit():
                        try:
                            del igrefrom[int(cmdli[1])]
                        except IndexError:
                            print("数组越界")
                            raise NameError("数组越界")
                        except:
                            print("格式错误")
                            raise NameError("格式错误")
                    else:
                        raise NameError("参数不明")
                    with open("ngaIgnore_dict.txt","w") as fa:
                        for i in igfrom:
                            fa.write(json.dumps({"type":"n","from":i})+"\n")
                    with open("ngaIgnore_dict.txt","a") as fa:      
                        for i in igrefrom:
                            fa.write(json.dumps({"type":"re","from":i})+"\n")
                except:
                    print("命令执行失败")
                    print("说明：\t删除忽略字典中指定的规则行")
                    print("\t请在使用前运行ld")
                    print("用法：\tdig 类型 序号")
                    print("序号请参考ld命令的返回，注意从0开始，并且每次删除后都会变动。")
                    print("\t其中类型包括re（正则表达式）和n（普通字串）")
                    print("样例：\tdig n 3")
                    print("\tdig re 0")#RE0还行


            elif cmd[:3]=="dtr":
                try:
                    cmdli=cmd[4:].split(" ")
                    if cmdli[0]=="n" and cmdli[1].isdigit():
                        try:
                            del trfrom[int(cmdli[1])]
                            del trto[int(cmdli[1])]
                        except IndexError:
                            print("数组越界")
                        except:
                            print("格式错误")
                    elif cmdli[0]=="re" and cmdli[1].isdigit():
                        try:
                            del trrefrom[int(cmdli[1])]
                            del trreto[int(cmdli[1])]
                        except IndexError:
                            print("数组越界")
                            raise NameError("数组越界")
                        except:
                            print("格式错误")
                            raise NameError("格式错误")
                    else:
                        raise NameError("参数不明")
                    with open("ngaTranslate_dict.txt","w") as fa:
                        for i in range(len(trfrom)):
                            fa.write(json.dumps({"type":"n","from":trfrom[i],"to":trto[i]})+"\n")
                    with open("ngaTranslate_dict.txt","a") as fa:      
                        for i in range(len(trrefrom)):
                            fa.write(json.dumps({"type":"re","from":trrefrom[i],"to":trreto[i]})+"\n")
                except:
                    print("命令执行失败")
                    print("说明：\t删除转义字典中指定的规则行")
                    print("\t请在使用前运行ld")
                    print("用法：\tdig 类型 序号")
                    print("序号请参考ld命令的返回，注意从0开始，并且每次删除后都会变动。")
                    print("\t其中类型包括re（正则表达式）和n（普通字串）")
                    print("样例：\tdtr n 3")
                    print("\tdtr re 1")


        #############################################save
            elif cmd[:4]=="save":
                print("此操作将会把剩余未处理的记录保存为文件，输入q以离开")
                askconf=input("按下回车以继续：")
                if askconf=="q":
                    continue
                else:
                    with open("给人看的结果.txt","w") as fwh:
                        fwh.write("舰娘当前计分：\n")
                        for i in range(len(self.kansens)):
                            fwh.write(self.kansens[i]+":"+str(self.votes[i])+"\n")
                        fwh.write("============================================\n")
                        fwh.write("楼层\t用户id\t评论内容\n")
                        with open("Result.json","w") as fw:
                            fw.write(json.dumps({"kansens":self.kansens,"votes":self.votes})+"\n")
                            for i in range(len(self.comment_process)):
                                fw.write(json.dumps({"floor":self.comment_ind[i],"user":self.users_id[i],"comment":self.comment_process[i]})+"\n")
                                fwh.write(str(self.comment_ind[i])+"\t"+str(self.users_id[i])+"\t"+self.comment_process[i]+"\n")
                    print("记录已经保存到当前目录")
                    print("Result.json可用于重载进度")
                    print("重载方法为重新启动本脚本")
                    print("并确保当前工作目录下存在Result.json")
                    
        #############################################addig
            elif cmd[:5]=="addig":
                try:
                    cmdli=cmd[6:].split(" ")
                    #print(cmdli)
                    print("添加类型：%s；关键字：%s"%(cmdli[0],cmdli[1]))
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
                    #print(cmdli)
                    print("添加类型：%s；查找关键字：%s；替换字符：%s"%(cmdli[0],cmdli[1],cmdli[2]))
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
                    #对列表进行子字符串处理，利用不知道什么排序
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

                    a1=len(trfrom)-1
                    a2=a1-1
                    doneli=[False for i in trfrom]
                    while a1>0:
                        a2=a1-1
                        while doneli[a1]:
                                a1-=1
                        while a2>0:
                            try:
                                tmp=trfrom[a1].index(trfrom[a2])
                                trfrom[a1],trfrom[a2]=swi(trfrom[a1],trfrom[a2])
                                trto[a1],trto[a2]=swi(trto[a1],trto[a2])
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
                    with open("ngaTranslate_dict.txt","w") as fa:
                        for i in range(len(trfrom)):
                            fa.write(json.dumps({"type":"n","from":trfrom[i],"to":trto[i]})+"\n")
                    with open("ngaTranslate_dict.txt","a") as fa:      
                        for i in range(len(trrefrom)):
                            fa.write(json.dumps({"type":"re","from":trrefrom[i],"to":trreto[i]})+"\n")
                    print("\n转义字典正则部分：")
                    print("序号\t表达式\t转换内容")
                    for i in range(len(trrefrom)):
                        print(str(i)+"\t"+trrefrom[i]+"\t"+trreto[i])
                    print("\n转义字典通常部分：")
                    print("序号\t关键字\t替换内容")
                    for i in range(len(trfrom)):
                        print(str(i)+"\t"+trfrom[i]+"\t"+trto[i])
                    print("\n忽略字典正则：")
                    print("序号\t表达式")
                    for i in range(len(igrefrom)):
                        print(str(i)+"\t"+igrefrom[i])
                    print("\n忽略字典通常：")
                    print("序号\t关键字")
                    for i in range(len(igfrom)):
                        print(str(i)+"\t"+igfrom[i])
                    # print(trrefrom)
                    # print(trreto)
                    # print(trfrom)
                    # print(trto)
                    # print(igrefrom)
                    # print(igfrom)

        ##############################################pass
            elif cmd[:4]=="pass":
                i=self.comment_process[0]
                tpi=i
                i=self.chkdic(i)
                while True:		
                    print(tpi+"的处理结果：")
                    for jj in range(len(self.kansens)):
                        print(str(jj)+" "+self.kansens[jj]+" "+str(self.cur_vote[jj]))
                
                    askconf=input("输入q以离开,或输入舰娘名或对应下标以修改此票，否则回车将此票计入:")
                    if askconf=="q":
                        break
                    try:
                        tag=self.kansens.index(askconf)
                        self.cur_vote[tag]=self.cur_vote[tag]^1
                    except:
                        pass
                    if askconf.isdigit():
                        try:
                            self.cur_vote[int(askconf)]=self.cur_vote[int(askconf)]^1
                        except IndexError:
                            print("数组越界")
                            continue
                    elif askconf=='':
                        if self.cur_vote.count(1)>3:
                            print("警告：当前投票对象大于3个")
                        self.votes=[self.votes[ii]+self.cur_vote[ii] for ii in range(len(self.votes))]
                        self.log.write("手动计票\t 楼层：%d\t字符：%s\n"%(self.comment_ind[0],self.comment_process[0]))
                        for ii in range(len(self.cur_vote)):
                            self.log.write(str(self.kansens[ii])+":"+str(self.cur_vote[ii])+"\n")
                        self.comment_process.pop(0)
                        self.users_id.pop(0)
                        self.comment_ind.pop(0)
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
                    i=self.comment_process[0]
                    tpi=i
                    i=self.chkdic(i)
                    print(i)
                    
        ##############################################auto
            elif cmd[:4]=="auto":
                print("此操作是自动处理投票记录，需先运行ld")
                cmdchr=input("输入q可返回，否则按回车继续：")
                if cmdchr=="q":
                    continue
                else:
                    inte=0
                    while inte < len(self.comment_process):
                        tpi=self.comment_process[inte]
                        i=self.chkdic(self.comment_process[inte])
                        if self.cur_vote.count(1)>3:
                            print("投票对象大于3个，%s作废"%tpi)
                            self.log.write("投票对象大于3个，%s作废\n"%tpi)
                            self.comment_process.pop(inte)
                            self.comment_ind.pop(inte)
                            self.users_id.pop(inte)
                            continue
                        elif i=='':
                            print("已处理\t%s"%tpi)
                            self.log.write("已处理\t%s:\n"%tpi)
                            for ii in range(len(self.cur_vote)):
                                self.log.write(str(self.kansens[ii])+":"+str(self.cur_vote[ii])+"\n")
                            self.votes=[self.votes[ii]+self.cur_vote[ii] for ii in range(len(self.votes))]
                            self.comment_process.pop(inte)
                            self.comment_ind.pop(inte)
                            self.users_id.pop(inte)
                        else:
                            inte+=1
                            
        ###############################################ato
            elif cmd[:3]=="ato":
                print("剩余%d条记录因无法完美匹配无法自动处理"%len(self.comment_process))
                
        ##############################################show
            elif cmd[:4]=="show":
                try:
                    showargv=int(cmd[5:])
                    if showargv>len(self.comment_process):
                        print("剩余记录数：%d；参数过大"%len(self.comment_process))
                        continue
                    for i in range(showargv):
                        print(self.comment_process[i])
                    continue
                except:
                    pass
                #print("show 欲显示的记录数；示例：")
                #print("show 23")
                print("默认打印最近5条无法自动处理的记录：")
                for i in range(5):
                    print(self.comment_process[i])
                    
        #############################################score
            elif cmd[:5]=="score":
                print("目前舰娘得票数：")
                for i in range(len(self.kansens)):
                    print(self.kansens[i]+"\t"+" "+str(self.votes[i]))
            else:
                print("无法理解的命令：%s"%cmd)
        self.log.close()

if __name__=="__main__":
    ngac=ngaC()
