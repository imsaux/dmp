# encode = utf-8

import wx


class ReplenishAddFrame(wx.Frame):
	def __init__(self, parent, id):
		wx.Frame.__init__(self, parent, -1, style = wx.DEFAULT_FRAME_STYLE)
		self.SetSize((400, 300))
		self.SetTitle('添加补充素材')
		self.parent = parent
		self.id = id
		self.ALL_SIZER = wx.BoxSizer(wx.VERTICAL)
		self.cb = list()
		self.tc1 = None
		self.tc2 = None
		self.tc3 = None
		self.tc4 = None
		self.ui_init()
		self.ui_bind()
		self.Show()

	def cb1(self, e):
		if e.IsChecked():
			if 1 not in self.cb:
				self.cb.append(1)
		else:
			if 1 in self.cb:
				self.cb.remove(1)

	def cb2(self, e):
		if e.IsChecked():
			if 2 not in self.cb:
				self.cb.append(2)
		else:
			if 2 in self.cb:
				self.cb.remove(2)

	def cb3(self, e):
		if e.IsChecked():
			if 3 not in self.cb:
				self.cb.append(3)
		else:
			if 3 in self.cb:
				self.cb.remove(3)

	def cb4(self, e):
		if e.IsChecked():
			if 4 not in self.cb:
				self.cb.append(4)
		else:
			if 4 in self.cb:
				self.cb.remove(4)




	def ui_init(self):
		panel = wx.Panel(self, -1)

		line_1 = wx.BoxSizer(wx.HORIZONTAL)
		cb1 = wx.CheckBox(panel, -1, "加噪")
		cb1.Bind(wx.EVT_CHECKBOX, self.cb1)
		self.tc1 = wx.TextCtrl(panel, -1, size=(100, -1))
		line_1.Add(cb1)
		line_1.Add(self.tc1)

		line_2 = wx.BoxSizer(wx.HORIZONTAL)
		cb2 = wx.CheckBox(panel, -1, "去噪")
		cb2.Bind(wx.EVT_CHECKBOX, self.cb2)
		self.tc2 = wx.TextCtrl(panel, -1, size=(100, -1))
		line_2.Add(cb2)
		line_2.Add(self.tc2)

		line_3 = wx.BoxSizer(wx.HORIZONTAL)
		cb3 = wx.CheckBox(panel, -1, "线性变换")
		cb3.Bind(wx.EVT_CHECKBOX, self.cb3)
		self.tc3 = wx.TextCtrl(panel, -1, size=(100, -1))
		line_3.Add(cb3)
		line_3.Add(self.tc3)

		line_4 = wx.BoxSizer(wx.HORIZONTAL)
		cb4 = wx.CheckBox(panel, -1, "非线性变换")
		cb4.Bind(wx.EVT_CHECKBOX, self.cb4)
		self.tc4 = wx.TextCtrl(panel, -1, size=(100, -1))
		line_4.Add(cb4)
		line_4.Add(self.tc4)

		btn1 = wx.Button(panel, -1, '确认')
		btn1.Bind(wx.EVT_BUTTON, self.btn1)
		self.ALL_SIZER.Add(line_1, 0, wx.EXPAND | wx.ALL | wx.CENTER | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		self.ALL_SIZER.Add(line_2, 0, wx.EXPAND | wx.ALL | wx.CENTER | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		self.ALL_SIZER.Add(line_3, 0, wx.EXPAND | wx.ALL | wx.CENTER | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		self.ALL_SIZER.Add(line_4, 0, wx.EXPAND | wx.ALL | wx.CENTER | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		self.ALL_SIZER.Add(btn1, 0, wx.ALIGN_CENTER, 0)
		panel.SetSizer(self.ALL_SIZER)

	def ui_bind(self):
		pass

	def btn1(self, e):
		for i in self.cb:
			v = getattr(self, 'tc'+str(i)).GetValue()
			print(i, ' -> ', v)
			# todo 对接传图
			# todo 对接图像处理
		self.Destroy()