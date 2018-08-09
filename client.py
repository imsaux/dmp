#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import os
import sys
import struct
import hashlib
import logging
import time
import json
import threading
import wx
import wx.xrc

def file_md5(filename):
    m_data = open(filename, 'rb')
    md5obj = hashlib.md5()
    md5obj.update(m_data.read())
    f_md5 = md5obj.hexdigest()
    m_data.close()
    return f_md5


class Send(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # 处理套接字异常
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            logging.error(e)
            sys.exit(1)
        self.s.connect((host, port))
    def send_bytes(self, operate, bdata, id):
        # 发送车轴信息
        self.s.send(b'b')
        recv = self.s.recv(100)
        data_json = json.dumps(bdata)
        data_json_len = struct.pack('ii10s', len(data_json), id, operate.encode())
        self.s.send(data_json_len)
        self.s.send(data_json.encode())

    def send_file(self, f, image_id, site, label_id = 0):
        # 发送文件
        self.s.send(b'i')
        recv = self.s.recv(100)
        # 解析协议
        if recv == b'ok':
            # 发送站名
            self.s.send(site.encode('utf-8'))
            if os.path.isfile(f):
                # 定义打包规则
                fhead = struct.pack('128slii', os.path.basename(f).encode('utf-8'), os.stat(f).st_size, image_id, label_id)
                self.s.send(fhead)
                # 判断接收量
                ret = self.s.recv(1024)  # 接收已经传了多少
                r = str(ret, encoding='utf-8')
                if r == 's':  # 文件不存在，从头开始传
                    has_send = 0
                else:  # 文件存在
                    has_send = int(r)
                fo = open(f, 'rb')
                fo.seek(has_send)  # 定位到已经传到的位置
                while has_send < os.stat(f).st_size:
                    filedata = fo.read(1024)
                    if not filedata:
                        break
                    self.s.send(filedata)
                fo.close()
                f_md5 = file_md5(f)
                server_file_md5 = self.s.recv(1024).decode()
                self.s.send(f_md5.encode())
                logging.info("client file md5:", f_md5)
                logging.info("server file md5:", server_file_md5)
            else:
                logging.error('file is not exist.')

        else:
            logging.error('connect break...')


# 数据导出
class Recv(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.f_dict = dict()

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            logging.error("Error creating socket: %s" % e)
            sys.exit(1)

        try:
            self.s.connect((host, port))
        except socket.gaierror as e:
            logging.error("Address-related error connecting to server: %s" % e)

        else:
            logging.info('connected server:', (host, port))


    def write_data(self,filename, filesize, recvd_size):
        # 文件写入
        if recvd_size == 0:
            mode = 'wb'
        else:
            mode = 'ab'
        with open(filename, mode) as f:
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    rdata = self.s.recv(1024)
                    recvd_size += len(rdata)
                else:
                    rdata = self.s.recv(filesize - recvd_size)
                    recvd_size = filesize
                f.write(rdata)

    def recv_file(self, ids, dir=''):
        self.s.send(b'o')
        recv = self.s.recv(100)
        if recv == b'ok':
            str_ids = json.dumps(ids)
            if len(dir) == 0:
                needfile = False
            else:
                needfile = True
            f_info = struct.pack('100s?',str_ids.encode(), needfile)
            self.s.send(f_info)
            recv_count = 0
            while True:
                # 定义文件信息
                fileinfo_size = struct.calcsize('128sl')
                buf = self.s.recv(fileinfo_size)
                if buf:
                    # 根据128sl解包文件信息，与client端的打包规则相同
                    filename, filesize = struct.unpack('128sl', buf)
                    # 使用strip()删除打包时附加的多余空字符
                    f_name = filename.decode('utf-8').strip('\00')
                    self.f_name = f_name
                    f_path = os.path.join(dir, f_name)
                    if needfile is True:
                        for root, dirs, files in os.walk(dir):
                            if f_name in files:
                                recvd_size = os.stat(f_path).st_size
                                self.s.sendall(str(recvd_size).encode('utf-8'))
                                self.write_data(f_path, filesize, recvd_size)
                                # md5文件校验
                                f_md5 = file_md5(f_path)
                                has_recv = int(recvd_size / filesize * 100)
                                self.f_dict[self.f_name] = has_recv

                                logging.info('receive:', has_recv, '%')
                                logging.info("client file md5:", f_md5)
                                self.s.send(f_md5.encode('utf-8'))
                                logging.info("server file md5:", self.s.recv(100).decode())

                            else:
                                # 定义接收了的文件大小
                                recvd_size = 0
                                self.s.sendall(bytes('s', encoding='utf-8'))
                                f = open(f_path, 'wb')
                                # 接收数据
                                while not recvd_size == filesize:
                                    if filesize - recvd_size > 1024:
                                        rdata = self.s.recv(1024)
                                        recvd_size += len(rdata)
                                    else:
                                        rdata = self.s.recv(filesize - recvd_size)
                                        recvd_size = filesize
                                    f.write(rdata)
                                has_recv = int(recvd_size / filesize * 100)
                                self.f_dict[self.f_name] = has_recv
                                logging.info('receive:', has_recv, '%')
                                f.close()
                                recv_count += 1
                                f_md5 = file_md5(f_path)
                                self.s.send(f_md5.encode('utf-8'))
                                logging.info('receive:', has_recv, '%')
                                logging.info("client file md5:", f_md5)
                                logging.info("server file md5:", self.s.recv(100).decode())

                    elif needfile is False:
                        recvd_size = 0
                        data = b''
                        while not recvd_size == filesize:
                            if filesize - recvd_size > 1024:
                                rdata = self.s.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = self.s.recv(filesize - recvd_size)
                                recvd_size = filesize
                            data += rdata
                        if len(data) == filesize:
                            logging.info('receive finish')
                        print(data)
                        return data
                else:
                    break

    def get_f(self):
        # 获取传输文件名及进度
        return self.f_dict


# class MyFrame(wx.Frame):
#
#     def __init__(self, parent, dic):
#         wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(600, 400), title = '进度监控')
#         self.SetForegroundColour(wx.Colour(0, 0, 0))
#         self.SetBackgroundColour(wx.Colour(255, 255, 255))
#         gbSizer = wx.GridBagSizer(0, 2)
#         gbSizer.SetFlexibleDirection(wx.BOTH)
#         gbSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
#         gbSizer.SetEmptyCellSize(wx.Size(600, 400))
#
#         self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"file_name", wx.DefaultPosition, wx.Size(400, 30), 0)
#         self.m_staticText1.Wrap(-1)
#         gbSizer.Add(self.m_staticText1, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)
#
#         self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"recved", wx.DefaultPosition, wx.Size(200, 30), 0)
#         self.m_staticText2.Wrap(-1)
#         gbSizer.Add(self.m_staticText2, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)
#         r = 0
#         for name,value in dic.items():
#             r += 1
#             c = 0
#             self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.Size(400, 30), 0)
#             self.m_staticText1.Wrap(-1)
#             gbSizer.Add(self.m_staticText1, wx.GBPosition(r, c), wx.GBSpan(1, 1), wx.ALL, 5)
#             c += 1
#             self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, str(value), wx.DefaultPosition, wx.Size(200, 30), 0)
#             self.m_staticText2.Wrap(-1)
#             gbSizer.Add(self.m_staticText2, wx.GBPosition(r, c), wx.GBSpan(1, 1), wx.ALL, 5)
#             self.SetSizer(gbSizer)
#             self.Layout()
#
# def main(c):
#     app = wx.App(False)
#     frame = MyFrame(None,c)
#     frame.Show(True)
#     app.MainLoop()


# a = Send('172.1.10.244', 9999)   # ip, port
# a.send_file('C:\\Users\\吕小凤\\Desktop\\test1\\mark\\TC64K_202.202.202.3_20180208054230_L057_57.jpg', 5, '杨柳青',1)   # 源文件路径,image_id,站名，label_id
# a.send_bytes('add',{'Cwheelcenter': '<Cwheelcenter = 100>', 'Cwheeloffset': '<Cwheeloffset = 200>', 'Ctop': '<Ctop = 300>', 'Cbottom': '<Cbottom = 400>', 'Cleft': '<Cleft = 500>', 'Cright': '<Cright = 600>', 'Crail': '<Crail = 700>'}, 7)
# a.send_bytes('delete',['Cbottom','Ctop'], 7)

# b = Recv('172.1.10.244', 9999)   # ip, port
# b.recv_file([1,4], 'C:\\yimi\\c_images')  #(保存路径，ids,True传文件，False传数据流)
# c=b.get_f()
# main(c)







