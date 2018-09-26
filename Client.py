# encode=utf-8

import Util
import json
import socket
import struct
import os
import threading


class Client:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.thread = threading.current_thread()

	def get_data(self, table_id, save_path, jpg_or_png=0, save_mode=0):
		# table_id -> 对应表id
		# jpg_or_png -> 0-jpg 1-png
		# save_path -> 保存文件夹
		# save_mode -> 0-生成文件 1-二进制数据
		lock = threading.Lock()
		i = 0
		while i < 3:
			try:
				s = socket.socket()
				s.connect((self.ip, self.port))
				lock.acquire()
				s.send(b'get')
				if s.recv(1) == b'r':
					s.send(struct.pack('li', table_id, jpg_or_png)) # 0-jpg 1-png
					if s.recv(2) == b't0':
						s.send(b't0')
						file_size, file_name = struct.unpack('Q100s', s.recv(1024))
						lock.release()
						file_name = file_name.split(b'\x00')[0].decode()
						lock.acquire()
						s.send(b'r')
						lock.release()
						_new_file_path = os.path.join(save_path, file_name)
						with open(_new_file_path, 'wb') as fw:
							while True:
								if file_size > 1024:
									lock.acquire()
									data = s.recv(1024)
									lock.release()
									fw.write(data)
								else:
									diff = 1024 - file_size
									lock.acquire()
									data = s.recv(diff)
									lock.release()
									fw.write(data)
									break
								file_size -= 1024
				lock.acquire()
				s.shutdown(2)
				s.close()
				del s
				lock.release()
				break
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('Client.get_data（%s）-> %s, %s, %s' % (
					str(self.thread.ident),
					str(table_id),
					save_path,
					str(jpg_or_png)))
				i += 1
				lock.acquire()
				s.shutdown(2)
				s.close()
				del s
				lock.release()

	def put_data(self, image_path, table_id, jpg_or_png=0):
		# image_path -> 本地图像路径
		# table_id -> 对应表id
		# jpg_or_png -> 0-jpg 1-png
		lock = threading.Lock()
		i = 0
		while i < 3:
			try:
				s = socket.socket()
				s.connect((self.ip, self.port))
				lock.acquire()
				s.send(b'put')
				_r = s.recv(1)
				lock.release()
				if _r == b'r':
					info = {
						'size': os.stat(image_path).st_size,
						'name': os.path.basename(image_path),
						'table_id': table_id,
						'mode': jpg_or_png
					}
					head_info = json.dumps(info)
					head_info_len = struct.pack('i', len(head_info))
					s.send(head_info_len)
					s.sendall(head_info)
					if s.recv(1) == b'r':
						with open(image_path, 'rb') as fr:
							data = fr.read()
							s.sendall(data)
					lock.release()
				s.shutdown(2)
				s.close()
				del s
				break
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('Client.put_data（%s）-> %s, %s, %s' % (str(self.thread.ident), str(table_id), image_path, str(jpg_or_png)))
				i += 1
				lock.acquire()
				s.shutdown(2)
				s.close()
				del s
				lock.release()
