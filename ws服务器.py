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
            os.chdir(os.getcwd()+"/../")
            targ="./"+''.join(random.sample("qwertyuiopasdfghjklzxcvbnm",10))
            print(targ)
            if os.path.exists("./%s"%targ):
                shutil.rmtree("./%s"%targ)
            os.makedirs(targ)
            for rt,ds,fs in os.walk("./kanmoecounter"):
                for f in fs:
                    src=os.path.join(rt,f)
                    shutil.copy(src,targ)
            os.chdir(os.getcwd()+'/'+targ)
            a=ngaC(self.connection)

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
