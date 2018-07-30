#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import os
import sys
import struct
import hashlib
import time


class Send(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # 处理套接字异常
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print("Error creating socket: %s" % e)
            sys.exit(1)
        # 处理连接套接字异常
        try:
            self.s.connect((host, port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" % e)
        else:
            print('connected server:', (host, port))

    def send_file(self, filepath):
        # s = init()
        # c_2_s('i')
        self.s.send(b'i')
        recv = self.s.recv(100)
        # 解析协议
        if recv == b'ok':
            print(recv)
            print('客户端发送文件，服务器接收文件')
            # 获取文件路径

            for root, dirs, files in os.walk(filepath):
                print(files)
                for file in files:
                    f = filepath + file
                    print(filepath + file)
                    #判断文件是否存在
                    if os.path.isfile(f):
                        # 定义打包规则
                        fileinfo_size = struct.calcsize('128sl')
                        # 定义文件头信息，包含文件名和文件大小
                        fhead = struct.pack('128sl', os.path.basename(f).encode('utf-8'), os.stat(f).st_size)
                        self.s.send(fhead)
                        print('client filepath: ', f)
                        # 判断接收量
                        ret = self.s.recv(1024)  # 接收已经传了多少
                        r = str(ret, encoding='utf-8')
                        if r == 's':  # 文件不存在，从头开始传
                            has_send = 0
                        else:  # 文件存在
                            has_send = int(r)
                        m = hashlib.md5()  # 创建md5校验
                        fo = open(f, 'rb')
                        fo.seek(has_send)  # 定位到已经传到的位置
                        while has_send < os.stat(f).st_size:
                            filedata = fo.read(1024)
                            if not filedata:
                                break
                            self.s.send(filedata)
                            m.update(filedata)
                        fo.close()
                        client_file_md5 = m.hexdigest()
                        print("client file md5:", client_file_md5)

# 数据导出
class Recv(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # 处理套接字异常
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print("Error creating socket: %s" % e)
            sys.exit(1)
        # 处理连接套接字异常
        try:
            self.s.connect((host, port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" % e)

        else:
            print('connected server:', (host, port))

    def recv_file(self, dir,ids):
        # s = init()
        # c_2_s('i')
        self.s.send(b'o')
        recv = self.s.recv(100)
        # while True:
        if recv == b'ok':
            print(recv)
            print('服务器发送文件，客户端接收文件')
            print(ids)
            # id = struct.pack('str',ids)
            idd = map(str, ids)
            #
            str_ids = "**".join(idd)
            print(str_ids)
            self.s.send(str_ids.encode())
            # id = struct.pack('ii', id1, id2)
            # self.s.send(id)

            while True:
                # 定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
                fileinfo_size = struct.calcsize('128sl')
                buf = self.s.recv(fileinfo_size)
                if buf:
                    # 根据128sl解包文件信息，与client端的打包规则相同
                    filename, filesize = struct.unpack('128sl', buf)
                    # 文件名长度为128，大于文件名实际长度
                    print('filesize is: ', filesize, 'filename size is: ', len(filename))
                    # 使用strip()删除打包时附加的多余空字符

                    f_name = filename.decode('utf-8').strip('\00')
                    f_path = dir + f_name
                    # filenewname = os.path.join(f_path, filename.decode('utf-8').strip('\00'))
                    print(f_path)
                    for root, dirs, files in os.walk(dir):
                        if f_name in files:
                            recvd_size = os.stat(f_path).st_size
                            self.s.sendall(str(recvd_size).encode('utf-8'))
                            with open(f_path, 'ab') as f:
                                while not recvd_size == filesize:
                                    if filesize - recvd_size > 1024:
                                        rdata = self.s.recv(1024)
                                        recvd_size += len(rdata)
                                    else:
                                        rdata = self.s.recv(filesize - recvd_size)
                                        recvd_size = filesize

                                    f.write(rdata)
                            f.close()
                            # md5文件校验
                            m_data = open(f_path,'rb')
                            md5obj = hashlib.md5()
                            md5obj.update(m_data.read())
                            hash = md5obj.hexdigest()
                            m_data.close()

                            print('receive:', int(recvd_size / filesize * 100), '%')
                            print("client file md5:", hash)
                            self.s.send(hash.encode('utf-8'))
                            print("server file md5:", self.s.recv(100).decode())

                        else:
                            # 定义接收了的文件大小
                            recvd_size = 0
                            self.s.sendall(bytes('s', encoding='utf-8'))
                            f = open(f_path, 'wb')
                            # 使用md5加密
                            m = hashlib.md5()
                            # 接收数据
                            while not recvd_size == filesize:
                                if filesize - recvd_size > 1024:
                                    rdata = self.s.recv(1024)
                                    recvd_size += len(rdata)
                                else:
                                    rdata = self.s.recv(filesize - recvd_size)
                                    recvd_size = filesize
                                # 递增接收数据并加密md5
                                m.update(rdata)
                                f.write(rdata)
                            self.s.send(m.hexdigest().encode('utf-8'))
                            print('receive:', int(recvd_size / filesize * 100), '%')
                            print("client file md5:", m.hexdigest())
                            print("server file md5:", self.s.recv(100).decode())

                            f.close()


# a = Send('172.1.10.244', 9999)   # ip, port
# a.send_file('C:/Users/吕小凤/Desktop/test1/')   # 源文件路径
#
b = Recv('172.1.10.244', 9999)   # ip, port
b.recv_file('C:/yimi/c_images/', [1,2,3,4])  #(保存路径，ids)







