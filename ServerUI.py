# -*- coding: utf-8 -*-
import Util
import time
import wx
import wx.adv
from six import BytesIO
import Server
import threading


def _get_icon():
	_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82'
	stream = BytesIO(_data)
	image = wx.Image(stream)
	bmp = wx.Bitmap(image)
	icon = wx.Icon()
	icon.CopyFromBitmap(bmp)
	return icon


class server_thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.stop_bit = False
		self.setDaemon(True)
		self.start()

	def set_stop_bit(self, v):
		self.stop_bit = v

	def run(self):
		serve = Server.ThreadedTCPServer((Server.IP, Server.PORT), Server.DmpTCPRequestHandler)
		serve.allow_reuse_address = True
		serve.daemon_threads = True
		with serve:
			_t = threading.Thread(target=serve.serve_forever)
			_t.daemon = True
			_t.start()

			while True:
				if self.stop_bit:
					break
				time.sleep(1)
			serve.shutdown()
			_t.join(3)



class MyTaskBarIcon(wx.adv.TaskBarIcon):

	def __init__(self, f):
		self.first = True
		wx.adv.TaskBarIcon.__init__(self)
		self.f = f
		self.ICON = _get_icon()
		self.ID_STOP = wx.NewId()
		self.ID_START = wx.NewId()
		self.ID_NONE = wx.NewId()
		self.TITLE = "数据管理平台"
		self.t = None
		self.SetIcon(wx.Icon(self.ICON), self.TITLE)
		self.Bind(wx.EVT_MENU, self.onStop, id=self.ID_STOP)
		self.Bind(wx.EVT_MENU, self.onStart, id=self.ID_START)

	def onStop(self, event):
		self.t.set_stop_bit(True)
		while self.t.isAlive():
			time.sleep(1)
		self.ShowBalloon(
			'通知',
			'已关闭！'
		)
		wx.CallAfter(self.Destroy)
		self.f.close()

	def onStart(self, event):
		self.t = server_thread()
		self.first = False
		self.ShowBalloon(
			'通知',
			'已启动程序！'
		)

	def CreatePopupMenu(self):
		menu = wx.Menu()
		for mentAttr in self.getMenuAttrs():
			menu.Append(mentAttr[1], mentAttr[0])
		return menu

	def getMenuAttrs(self):
		if self.first:
			return [('启动', self.ID_START),
			        ('退出', self.ID_STOP)]
		else:
			if self.t is not None and self.t.isAlive():
				return [('已启动', self.ID_NONE),
				        ('退出', self.ID_STOP)]


class MyFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self)


class MyApp(wx.App):
	def OnInit(self):
		f = MyFrame()
		MyTaskBarIcon(f)
		return True


if __name__ == "__main__":
	app = MyApp()
	app.MainLoop()
