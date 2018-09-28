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
        _msg = '%s 已连接' % (repr(self.client_address))
        print(_msg)
        Util.LOG.info(_msg)
        lock.acquire()
        _cmd = str(self.request.recv(3), encoding="utf-8")
        lock.release()
        if _cmd == "get":  # s -> c
            lock.acquire()
            self.request.send(b'r')
            table_id, jpg_or_png = struct.unpack('li', self.request.recv(1024))
            lock.release()
            print('id -> %s, jpg_or_png -> %s (%s)' % (str(table_id), str(jpg_or_png), repr(self.client_address)))
            try:
                lock.acquire()
                _path = ''
                if jpg_or_png == 0:
                    _path = Util.execute_sql('select dmp.image.path from dmp.image where dmp.image.id=%s', args=table_id)[0][0]
                elif jpg_or_png == 1:
                    _path = Util.execute_sql(
                        'select dmp.r_image_label.data  from dmp.r_image_label where dmp.r_image_label.id=%s',
                        args=table_id)[0][0]
                lock.release()
                if os.path.exists(os.path.normpath(_path)):
                    lock.acquire()
                    self.request.send(b't0')
                    if self.request.recv(2) == b't0':
                        file_size = os.stat(_path).st_size
                        self.request.send(struct.pack('Q100s', file_size, os.path.basename(_path).encode()))
                        print('path -> %s, size -> %s (%s)' % (
                            os.path.normpath(_path),
                            str(file_size),
                            repr(self.client_address)
                        ))
                        if self.request.recv(1) == b'r':
                            fr = open(_path, 'rb')
                            data = fr.read()
                            self.request.sendall(data)
                            fr.close()
                    lock.release()
                else:
                    Util.LOG.error('客户端请求的图像不存在！-> %s' % (str(table_id)))
            except Exception as e:
                Util.LOG.error(repr(e))
                Util.LOG.debug('params -> %s, %s, %s' % (str(table_id), _path, str(file_size)))
            self.request.send(b'over')
        if _cmd == "put":  # c -> s
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
                if jpg_or_png == 0:  # jpg
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
            except Exception as e:
                Util.LOG.debug(repr(e))

            Util.LOG.debug('file_size, file_name， table_id, jpg_or_png-> %s, %s, %s, %s' % (
            str(file_size), file_name, str(table_id), str(jpg_or_png)))
            _new_file_path = os.path.join(_save_path, file_name)
            Util.LOG.debug('传输保存路径 -> %s' % (_new_file_path,))
            lock.acquire()
            self.request.send(b'r')
            fw = open(_new_file_path, 'wb')
            try:
                data = b''
                while True:
                    _d = self.request.recv(1024)
                    if not _d:
                        break
                    data += _d
                fw.write(data)
            except Exception as e:
                Util.LOG.error(repr(e))
            finally:
                fw.close()
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
            finally:
                if lock.locked():
                    lock.release()
            self.request.send(b'over')
        _msg = '%s 已断开' % (repr(self.client_address))
        print(_msg)
        Util.LOG.info(_msg)

    def _check_dir(self, _mode, _site, _code, _date):
        if not os.path.exists(_root):
            return None
        if not os.path.exists(os.path.join(_root, _mode)):
            os.makedirs(os.path.join(_root, _mode))
        if not os.path.exists(os.path.join(_root, _mode, _site)):
            os.makedirs(os.path.join(_root, _mode, _site))
        if not os.path.exists(os.path.join(_root, _mode, _site, _code[:2])):
            os.makedirs(os.path.join(_root, _mode, _site, _code[:2]))
        if not os.path.exists(os.path.join(_root, _mode, _site, _code[:2], str(_date.year))):
            os.makedirs(os.path.join(_root, _mode, _site, _code[:2], str(_date.year)))
        return True


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


with  ThreadedTCPServer((IP, PORT), DmpTCPRequestHandler) as serve:
    serve.allow_reuse_address = True
    serve.daemon_threads = True
    serve.serve_forever()
