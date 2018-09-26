# encode=utf-8

import Util
import json
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
		Util.LOG.info('%s 已连接' % (repr(self.client_address)))
		_cmd = str(self.request.recv(3), encoding="utf-8")
		if _cmd == "get": # s -> c
			self.request.send(b'r')
			table_id, jpg_or_png = struct.unpack('li', self.request.recv(1024))
			try:
				_path = ''
				if jpg_or_png == 0:
					_path = Util.execute_sql('select dmp.image.path from dmp.image where dmp.image.id=%s', args=table_id)[0][0]
				elif jpg_or_png == 1:
					_path = Util.execute_sql('select dmp.r_image_label.data  from dmp.r_image_label where dmp.r_image_label.id=%s', args=table_id)[0][0]
				if os.path.exists(os.path.normpath(_path)):
					self.request.send(b't0')
					if self.request.recv(2) == b't0':
						file_size = os.stat(_path).st_size
						self.request.send(struct.pack('Q100s', file_size, os.path.basename(_path).encode()))
						if self.request.recv(1) == b'r':
							with open(_path, 'rb') as fr:
								while True:
									data = fr.read(1024)
									if not data:
										break
									self.request.send(data)
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('params -> %s, %s, %s' % (str(table_id), _path, str(file_size)))
		if _cmd == "put": # c -> s
			lock.acquire()
			self.request.send(b'r')
			_data = self.request.recv(struct.calcsize('i'))
			lock.release()
			head_info_len = struct.unpack('i', _data)[0]
			data = self.request.recv(head_info_len)
			head_info = json.loads(data, encoding='utf-8')
			table_id = head_info['table_id']
			jpg_or_png = head_info['mode']
			file_name = head_info['name']
			file_size = head_info['size']
			try:
				_site, _code, _date = '', '', ''
				lock.acquire()
				if jpg_or_png == 0: # jpg
					_site, _code, _date = Util.execute_sql(
						'select dmp.image.site, dmp.image.code, dmp.image.date from dmp.image where dmp.image.id=%s',
						args=table_id)[0]
				elif jpg_or_png == 1:
					_site, _code, _date = Util.execute_sql(
						'select dmp.image.site, dmp.image.code, dmp.image.date from dmp.image where dmp.image.id=(select dmp.r_image_label.image_id  from dmp.r_image_label where dmp.r_image_label.id=%s)',
						args=table_id)[0]
				lock.release()
				_kind = _code[:2]
				_year = _date.year
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
			except Exception as e:
				Util.LOG.debug(repr(e))

			Util.LOG.debug('file_size, file_name， table_id, jpg_or_png-> %s, %s, %s, %s' % (str(file_size), file_name, str(table_id), str(jpg_or_png)))
			lock.acquire()
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
			lock.release()
			_update_sql = ''
			if jpg_or_png == 0:
				_update_sql = 'update dmp.image set dmp.image.path=%s where dmp.image.id=%s'
			elif jpg_or_png == 1:
				_update_sql = 'update dmp.r_image_label set dmp.r_image_label.data=%s where dmp.r_image_label.id=%s'
			try:
				lock.acquire()
				Util.execute_sql(_update_sql, args=(_new_file_path, table_id), need_commit=True)
				lock.release()
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('params -> %s, %s' % (_new_file_path, table_id))

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
