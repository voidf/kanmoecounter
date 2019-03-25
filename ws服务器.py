#-*- coding:utf8 -*-

import threading
import hashlib
import socket
import base64
import struct
import os,traceback,shutil,random
from ngaClass import ngaC
global clients
clients = {}

#参考链接（服务器框架）：https://www.cnblogs.com/lichmama/p/3931212.html
#参考链接（解决中文问题）：https://www.cnblogs.com/wangqj1996/p/9244601.html

#客户端处理线程
class websocket_thread(threading.Thread):
    def __init__(self, connection, username):
        super(websocket_thread, self).__init__()
        self.connection = connection
        self.username = username
    
    def run(self):
        print(self)
        try:
            print( 'new websocket client joined!')
            data = self.connection.recv(8192)
            headers = self.parse_headers(data)
            #print(headers)
            token = self.generate_token(headers[b'Sec-WebSocket-Key'])
            self.connection.send(b'\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % token)

            #os.system("pause")
            targ="./"+''.join(random.sample("qwertyuiopasdfghjklzxcvbnm",10))
            print(targ)
            os.chdir(os.getcwd()+"/../")
            if os.path.exists("./%s"%targ):
                shutil.rmtree("./%s"%targ)
            os.makedirs(targ)
            for rt,ds,fs in os.walk("./kanmoecounter"):
                for f in fs:
                    src=os.path.join(rt,f)
                    shutil.copy(src,targ)
            os.chdir(os.getcwd()+'/'+targ)
            a=ngaC(self.connection)
            
            clients.pop(self.username)
            os.chdir(os.getcwd()+"/../")
            shutil.rmtree("./%s"%targ)

        except socket.timeout:
            print("连接超时，清除连接")
            clients.pop(self.username)
            os.chdir(os.getcwd()+"/../")
            shutil.rmtree("./%s"%targ)
        except ImportError:
            print("客户端已经离线")
            clients.pop(self.username)
            os.chdir(os.getcwd()+"/../")
            shutil.rmtree("./%s"%targ)
        except Exception as e:
            print("未知错误")
            clients.pop(self.username)
            traceback.print_exc()
            os.chdir(os.getcwd()+"/../")
            shutil.rmtree("./%s"%targ)

    #payload=我his都护府我阿是U有覅U暗示法开始开后方可试试看觉得好看福建省的会客室可返回看还是得夸海口市哈克龙圣诞好疯狂安徽水利返回斯柯达后方可绝对是开始哈克龙合法看来是哈卡莱双刀很快就是东方红可视电话孤苦伶仃是好看的是腹黑刚看电视费好更快的发挥高科技的份上花开电风扇换个快递费上过课单方事故开电风扇和广阔的发舒肝颗粒的算法好更快等方式给对方看脚后跟的饭卡手机号广阔的副书记和广阔的福建省看的复合弓一有hi，工行卡的健身房个花开电风扇和广东省房和刚开始的华工科技的算法和高科技的份上和高科技的份上换个看见山顶好看3432534257324658429365973246578346592670971209347329879283598716 经核实高考结束的和客观地说黑客攻击东方红开关机第四课广泛的精华第三方开个会的首付款更好地富士康和关键靠方大化工扩容一问题一二五义务和V就肯定会V就可好看V后肯定会各科室V看就看V看见hi义务热月很快就啊哈卡洛斯后方可圣诞节阿里和喀什啥都看画风我我阿姨覅地理福尔IE攘夷U而爱UR额hi和认可看似简单快删掉还是搞活动粉丝个华东师范换个谁的看是发动机开发速度快速度快水电费水电费等我his都护府我阿是U有覅U暗示法开始开后方可试试看觉得好看福建省的会客室可返回看还是得夸海口市哈克龙圣诞好疯狂安徽水利返回斯柯达后方可绝对是开始哈克龙合法看来是哈卡莱双刀很快就是东方红可视电话孤苦伶仃是好看的是腹黑刚看电视费好更快的发挥高科技的份上花开电风扇换个快递费上过课单方事故开电风扇和广阔的发舒肝颗粒的算法好更快等方式给对方看脚后跟的饭卡手机号广阔的副书记和广阔的福建省看的复合弓一有hi，工行卡的健身房个花开电风扇和广东省房和刚开始的华工科技的算法和高科技的份上和高科技的份上换个看见山顶好看3432534257324658429365973246578346592670971209347329879283598716 经核实高考结束的和客观地说黑客攻击东方红开关机第四课广泛的精华第三方开个会的首付款更好地富士康和关键靠方大化工扩容一问题一二五义务和V就肯定会V就可好看V后肯定会各科室V看就看V看见hi义务热月很快就啊哈卡洛斯后方可圣诞节阿里和喀什啥都看画风我我阿姨覅地理福尔IE攘夷U而爱UR额hi和认可看似简单快删掉还是搞活动粉丝个华东师范换个谁的看是发动机开发速度快速度快水电费水电费等

    def parse_headers(self, msg):
        headers = {}

        header, data = msg.split(b'\r\n\r\n', 1)
        for line in header.split(b'\r\n')[1:]:
            key, value = line.split(b': ', 1)
            headers[key] = value
        headers['data'] = data
        return headers

    def generate_token(self, msg):
        print( 'msg is:')
        print( msg)
        key = msg + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key).digest()
        return base64.b64encode(ser_key)

#服务端
class websocket_server(threading.Thread):
    def __init__(self, port):
        super(websocket_server, self).__init__()
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.port))
        sock.listen(256)
        print( 'websocket server started!')
        while True:
            connection, address = sock.accept()
            print(threading.active_count())
            try:
                username = "ID" + str(address[1])
                
                thread = websocket_thread(connection, username)
                thread.start()
                #print("运行中的线程:",thread)
                connection.settimeout(2400)
                clients[username] = connection

            except socket.timeout:
                print( 'websocket connection timeout!')

if __name__ == '__main__':
    server = websocket_server(9000)
    server.start()
