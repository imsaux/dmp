# encode=utf-8

import socket
import struct
import os
import threading
import Util


lock = threading.Lock()


class Client:
	def __init__(self, ip, port):
		self.s = socket.socket()
		self.ip = ip
		self.port = port
		self.thread = threading.current_thread()

	def get_data(self, table_id, save_path, jpg_or_png=0, save_mode=0):
		# table_id -> 对应表id
		# jpg_or_png -> 0-jpg 1-png
		# save_path -> 保存文件夹
		# save_mode -> 0-生成文件 1-二进制数据
		Util.LOG.info('Client.get_data（%s）-> %s, %s, %s' % (str(self.thread.ident), str(table_id), save_path, str(jpg_or_png)))
		self.s.connect((self.ip, self.port))
		lock.acquire()
		self.s.send(b'get')
		if self.s.recv(1) == b'r':
			self.s.send(struct.pack('li', table_id, jpg_or_png)) # 0-jpg 1-png
			if self.s.recv(2) == b't0':
				self.s.send(b't0')
				file_size, file_name = struct.unpack('Q100s', self.s.recv(1024))
				lock.release()
				file_name = file_name.split(b'\x00')[0].decode()
				lock.acquire()
				self.s.send(b'r')
				lock.release()
				_new_file_path = os.path.join(save_path, file_name)
				with open(_new_file_path, 'wb') as fw:
					while True:
						if file_size > 1024:
							lock.acquire()
							data = self.s.recv(1024)
							lock.release()
							fw.write(data)
						else:
							diff = 1024 - file_size
							lock.acquire()
							data = self.s.recv(diff)
							lock.release()
							fw.write(data)
							break
						file_size -= 1024
		self.s.shutdown(2)
		self.s.close()

	def put_data(self, image_path, table_id, jpg_or_png=0):
		# image_path -> 本地图像路径
		# table_id -> 对应表id
		# jpg_or_png -> 0-jpg 1-png
		Util.LOG.info('Client.put_data（%s）-> %s, %s, %s' % (str(self.thread.ident), str(table_id), image_path, str(jpg_or_png)))
		self.s.connect((self.ip, self.port))
		lock.acquire()
		self.s.send(b'put')
		if self.s.recv(1024) == b'r':
			self.s.send(struct.pack('li', table_id, jpg_or_png)) # 0-jpg 1-png
			if self.s.recv(1024) == b't0':
				lock.release()
				file_size = os.stat(image_path).st_size
				lock.acquire()
				self.s.send(struct.pack('Q100s', file_size, os.path.basename(image_path).encode()))
				if self.s.recv(1024) == b'r':
					lock.release()
					try:
						with open(image_path, 'rb') as fr:
							while True:
								data = fr.read(1024)
								if not data:
									break
								lock.acquire()
								self.s.send(data)
								lock.release()
					except Exception as e:
						Util.LOG.error(repr(e))
		self.s.shutdown(2)
		self.s.close()