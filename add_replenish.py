# encode = utf-8

import wx
import wx.lib.scrolledpanel as scrolled
import StatisticsView
import wx.dataview as dv

class ReplenishAdd(scrolled.ScrolledPanel):
	def __init__(self, parent, log, objects=None, ids=None, statistics_data=None, data_view_obj=None, main_view_obj=None):
		# objects 选择的检测项
		# ids 原图id列表
		# statistics_data 已有统计数据
		scrolled.ScrolledPanel.__init__(self, parent, -1)
		self.parent = parent
		self.log = log
		self.objects = objects
		self.main = main_view_obj
		self.dataview = data_view_obj
		self.ids = ids
		self.statistics_data = statistics_data
		self.Setting_Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Information_Sizer = wx.BoxSizer(wx.VERTICAL)
		self.ALL_SIZER = wx.BoxSizer(wx.HORIZONTAL)
		self.ui_init()
		self.ALL_SIZER.Add(self.Setting_Sizer)
		self.ALL_SIZER.Add(self.Information_Sizer, 3, wx.EXPAND | wx.ALL)
		self.SetSizer(self.ALL_SIZER)
		self.SetupScrolling()

	def ui_init(self):
		for item in self.objects:
			_tmp = list()
			box_object_title = wx.StaticBox(self, -1, item)
			box_object = wx.StaticBoxSizer(box_object_title, wx.VERTICAL)
			grid_object = wx.FlexGridSizer(cols=2)

			st = wx.StaticText(self, -1, "启用")
			cb = wx.CheckBox(self, -1, '')
			setattr(self, item + '_cb', cb)
			_tmp.append((st, cb))

			st = wx.StaticText(self, -1, "加噪")
			tc = wx.TextCtrl(self, -1)
			setattr(self, item + '_tc1', tc)
			_tmp.append((st, tc))

			st = wx.StaticText(self, -1, "去噪")
			tc = wx.TextCtrl(self, -1)
			setattr(self, item + '_tc2', tc)
			_tmp.append((st, tc))

			st = wx.StaticText(self, -1, "线性变换")
			tc = wx.TextCtrl(self, -1)
			setattr(self, item + '_tc3', tc)
			_tmp.append((st, tc))

			st = wx.StaticText(self, -1, "非线性变换")
			tc = wx.TextCtrl(self, -1)
			setattr(self, item + '_tc4', tc)
			_tmp.append((st, tc))

			for item1, item2 in _tmp:
				grid_object.Add(item1, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)
				grid_object.Add(item2, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5)

			box_object.Add(grid_object, 0, wx.LEFT|wx.ALL, 5)
			self.Setting_Sizer.Add(box_object, 0, wx.LEFT|wx.ALL, 5)

		_bt_sizer = wx.BoxSizer()
		bt1 = wx.Button(self, -1, '预览')
		bt2 = wx.Button(self, -1, '确定')
		bt1.Bind(wx.EVT_BUTTON, self.review)
		bt2.Bind(wx.EVT_BUTTON, self.doit)

		_bt_sizer.Add(bt1, 1, wx.ALIGN_CENTER_HORIZONTAL, 15)
		_bt_sizer.Add(bt2, 1, wx.ALIGN_CENTER_HORIZONTAL, 15)
		self.Information_Sizer.Add(_bt_sizer, 0, wx.ALIGN_CENTER, 10)

		self.dvc = dv.DataViewListCtrl(self, style=wx.BORDER_THEME | dv.DV_ROW_LINES | dv.DV_VERT_RULES | dv.DV_MULTIPLE)
		self.dvc.SetSize((400, 300))
		self.dvc.AppendTextColumn('项', width=100)
		self.dvc.AppendTextColumn('值', width=100)
		self.Information_Sizer.Add(self.dvc, 1, wx.EXPAND|wx.ALL|wx.LEFT|wx.RIGHT|wx.TOP, 10)

	def review(self, e):
		import copy
		_tmp = copy.deepcopy(self.statistics_data)
		_work = self.get_work()
		for _id in _work.keys():
			for obj in _work[_id].keys():
				_sum = sum(_work[_id][obj])
				for i in range(len(_tmp)):
					if _tmp[i][0] == obj:
						_new_value = (obj, str(_tmp[i][1]+_sum*_tmp[i][1]) + ' （含补充素材 ' + str(_sum*_tmp[i][1]) + ' ）')
						_tmp[i] = _new_value
		self.dvc.DeleteAllItems()
		for i in _tmp:
			self.dvc.AppendItem(i)

	def get_work(self):
		self.replenish_value = dict()
		for ctrl in dir(self):
			if '_cb' in ctrl:
				if getattr(self, ctrl).IsChecked():
					name = ctrl.split('_')[0] + '_tc'
					v = list()
					for i in range(4):
						ctl = getattr(self, name + str(i+1))
						if ctl.GetValue() != '':
							try:
								v.append(int(ctl.GetValue()))
							except Exception as e:
								v.append(0)
					self.replenish_value[ctrl.split('_')[0]] = v
		works = dict()
		for key in self.replenish_value.keys():
			_id = self.get_id_by_label(key)
			if _id is not None:
				for i in _id:
					if i not in works.keys():
						works[i] = dict()
					works[i][key] = self.replenish_value[key]
		return works

	def get_in_sql(self, iters):
		_in_ = ''
		for item in iters:
			if _in_ == '':
				_in_ += '"' + str(item) + '"'
			else:
				_in_ += ',"' + str(item) + '"'
		return 'in(' + _in_ + ')'
	
	def get_id_by_label(self, lbl):
		_in = self.get_in_sql(self.ids)
		# _sql = 'select image_id from dmp.r_image_label where image_id ' + _in + ' and label_id in(select id from dmp.label where name="' + lbl_name + '")'
		_sql = 'select image_id from dmp.r_image_label where image_id ' + _in + ' and label_id in(select id from dmp.label where name="' + lbl.split('-')[0] + '" and type="' + lbl.split('-')[1] + '")'
		if self.main is None:
			return None
		data = self.main.db_do_sql(_sql)
		if len(data) > 0:
			return [i[0] for i in data]
		else:
			return None

	def doit(self, e):
		_work = self.get_work()
		if self.dataview is not None:
			self.dataview.set_replenish_data(_work)
		self.parent.Destroy()