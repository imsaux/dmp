# encode=utf-8

import Util
import socketserver
import os
import struct
import threading

_root = Util.ROOT_DIR
IP = Util.HOST
PORT = Util.PORT
lock = threading.Lock()


class DmpTCPRequestHandler(socketserver.BaseRequestHandler):
	def handle(self):
		# if Util.db is None:
		# 	return
		_cmd = str(self.request.recv(1024), encoding="utf-8")
		if _cmd == "get": # s -> c
			self.request.send(b'r')
			table_id, jpg_or_png = struct.unpack('li', self.request.recv(1024))
			try:
				_path = ''
				if jpg_or_png == 0:
					_path = Util.execute_sql('select dmp.image.path from dmp.image where dmp.image.id=%s', args=table_id)[0][0]
				elif jpg_or_png == 1:
					_path = Util.execute_sql('select dmp.r_image_label.data  from dmp.r_image_label where dmp.r_image_label.id=%s', args=table_id)[0][0]
				if not os.path.exists(_path):
					Util.LOG.debug('无效路径')
					Util.LOG.debug(repr(_path))
					return
			except Exception as e:
				Util.LOG.error(repr(e))
				return
			self.request.send(b't0')
			if self.request.recv(2) == b't0':
				file_size = os.stat(_path).st_size
				self.request.send(struct.pack('Q100s', file_size, os.path.basename(_path).encode()))
				if self.request.recv(1) == b'r':
					try:
						with open(_path, 'rb') as fr:
							while True:
								data = fr.read(1024)
								if not data:
									break
								self.request.send(data)
					except Exception as e:
						Util.LOG.error(repr(e))
		elif _cmd == "put": # c -> s
			self.request.send(b'r')
			table_id, jpg_or_png = struct.unpack('li', self.request.recv(1024))
			Util.LOG.debug('table_id, jpg_or_png -> %s, %s' % (table_id, jpg_or_png))
			try:
				lock.acquire()
				_site, _code, _date = '', '', ''
				if jpg_or_png == 0: # jpg
					_site, _code, _date = Util.execute_sql(
						'select dmp.image.site, dmp.image.code, dmp.image.date from dmp.image where dmp.image.id=%s',
						args=table_id)[0]
				elif jpg_or_png == 1:
					_site, _code, _date = Util.execute_sql(
						'select dmp.image.site, dmp.image.code, dmp.image.date from dmp.image where dmp.image.id=(select dmp.r_image_label.image_id  from dmp.r_image_label where dmp.r_image_label.id=%s)',
						args=table_id)[0]
				lock.release()
			except Exception as e:
				Util.LOG.debug(repr(e))
			_kind = _code[:2]
			_year = _date.year
			self.request.send(b't0')
			file_size, file_name = struct.unpack('Q100s', self.request.recv(1024))
			file_name = file_name.split(b'\x00')[0].decode()
			Util.LOG.debug('file_size, file_name -> %s, %s' % (file_size, file_name))
			_mode = '原图' if jpg_or_png == 0 else '标签'
			_save_path = os.path.join(
				_root,
				_mode,
				_site,
				_kind,
				str(_year)
			)
			if not self._check_dir(_mode, _site, _code, _date):
				Util.LOG.error('传输保存路径异常')
			_new_file_path = os.path.join(_save_path, file_name)
			Util.LOG.debug('传输保存路径 -> %s' % (_new_file_path,))
			self.request.send(b'r')
			with open(_new_file_path, 'wb') as fw:
				while True:
					if file_size > 1024:
						data = self.request.recv(1024)
						fw.write(data)
					else:
						diff = 1024 - file_size
						data = self.request.recv(diff)
						fw.write(data)
						break
					file_size -= 1024
			_update_sql = ''
			if jpg_or_png == 0:
				_update_sql = 'update dmp.image set dmp.image.path=%s where dmp.image.id=%s'
			elif jpg_or_png == 1:
				_update_sql = 'update dmp.r_image_label set dmp.r_image_label.data=%s where dmp.r_image_label.id=%s'
			try:
				Util.execute_sql(_update_sql, args=(_new_file_path, table_id), need_commit=True)
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('params -> %s, %s' % (_new_file_path, table_id))
		else:
			pass

	def _check_dir(self, _mode, _site, _code, _date):
		if not os.path.exists(_root):
			return None
		if not os.path.exists(os.path.join(_root, _mode)):
			os.makedirs(os.path.join(_root, _mode))
		if not os.path.exists(os.path.join(_root, _mode, _site)):
			os.makedirs(os.path.join(_root, _mode, _site))
		if not  os.path.exists(os.path.join(_root, _mode, _site, _code[:2])):
			os.makedirs(os.path.join(_root, _mode, _site, _code[:2]))
		if not  os.path.exists(os.path.join(_root, _mode, _site, _code[:2], str(_date.year))):
			os.makedirs(os.path.join(_root, _mode, _site, _code[:2], str(_date.year)))
		return True


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass


with  ThreadedTCPServer((IP, PORT), DmpTCPRequestHandler) as serve:
	serve.allow_reuse_address = True
	serve.daemon_threads = True
	serve.serve_forever()
