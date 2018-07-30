# encoding=utf-8
import wx
import wx.dataview as dv


class StatisticsView(wx.Panel):
	def __init__(self, parent, data=None, mode=None):
		wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		self.data = data
		self.mode = mode
		self._all_data = []
		self.re_fill_enable = True
		self.can_repeat = None
		self.dvc = dv.DataViewListCtrl(self,
		                               style=wx.BORDER_THEME
		                                     | dv.DV_ROW_LINES  # nice alternating bg colors
		                                     | dv.DV_VERT_RULES
		                                     | dv.DV_MULTIPLE
		                               )

		self.dvc.AppendTextColumn('项', width=100)
		self.dvc.AppendTextColumn('值', width=100)
		if self.data is not None:
			self.fill_data()
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(self.dvc, 1, wx.EXPAND)

		# b1 = wx.Button(self, label="刷新", name="refresh")
		# self.Bind(wx.EVT_BUTTON, self.on_refresh, b1)
		b2 = wx.Button(self, label="返回", name="first")
		self.Bind(wx.EVT_BUTTON, self.on_first, b2)
		# b3 = wx.Button(self, label="导出", name="export")
		# self.Bind(wx.EVT_BUTTON, self.on_export, b3)

		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		# btnbox.Add(b1, 0, wx.LEFT|wx.RIGHT, 5)
		btnbox.Add(b2, 0, wx.LEFT | wx.RIGHT, 5)
		# btnbox.Add(b3, 0, wx.LEFT|wx.RIGHT, 5)
		self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
		self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_refill_data)

	def fill_data(self, refresh=False, need_clear=True):
		if need_clear:
			self.clear_data()
		self._all_data = list()
		for id in [x[0] for x in self.data]:
			_sql = "SELECT (select concat(l.name,'-', l.type) from dmp.label l where id=ril.label_id), count(label_id), image_id FROM dmp.r_image_label ril where image_id=" + str(
				id) + "  group by label_id, image_id;"
			self._all_data.append(self.parent.db_do_sql(_sql))
		if refresh:
			_in_ = ''
			for i in [x[0] for x in self.data]:
				if _in_ == '':
					_in_ += '"' + str(i) + '"'
				else:
					_in_ += ',"' + str(i) + '"'

			_sql = 'select * from dmp.image where id in(' + _in_ + ')'
			self.parent.db_do_sql(_sql, update=True)

		self.sum_result(self._all_data)
		self.re_fill_enable = True

	def sum_result(self, data):
		_sum_ = dict()
		has_item = False
		for i in range(self.dvc.ItemCount):
			if self.dvc.GetValue(i, 0) == '素材数量':
				self.dvc.SetValue(int(self.dvc.GetValue(i, 1)) + len(data), i, 1)
				has_item = True
		if not has_item:
			self.dvc.AppendItem(['素材数量', len(data)])
		for item in data:
			if len(item) > 0:
				for i in item:
					if '-' in i[0]:
						if len(self.parent.last_query_objects) == 0:
							if i[0] not in _sum_.keys():
								_sum_[i[0]] = 0
							_sum_[i[0]] += i[1]
						elif len(self.parent.last_query_objects) > 0 and i[0].split('-')[
							0] in self.parent.last_query_objects:
							if i[0] not in _sum_.keys():
								_sum_[i[0]] = 0
							_sum_[i[0]] += i[1]
		for key in _sum_.keys():
			has_item = False
			for i in range(self.dvc.ItemCount):
				if self.dvc.GetValue(i, 0) == key:
					self.dvc.SetValue(int(self.dvc.GetValue(i, 1)) + _sum_[key], i, 1)
					has_item = True
			if not has_item:
				self.dvc.AppendItem([key, _sum_[key]])

	def on_refill_data(self, event):
		item = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 0)
		if item != '素材数量':
			if self.re_fill_enable:
				self.re_fill_data(item)

		event.Skip()

	def clear_data(self):
		self.dvc.DeleteAllItems()

	def re_fill_data(self, item, need_clear=True):
		if need_clear:
			self.clear_data()
		items = []
		ids = []
		for x in [x for x in self._all_data if len(x) > 0]:
			for y in x:
				if y[0] == item:
					items.append(x)
					ids.append(y[2])
		self.sum_result(items)
		_in_ = ''
		if len(ids) > 0:
			for i in ids:
				if _in_ == '':
					_in_ += '"' + str(i) + '"'
				else:
					_in_ += ',"' + str(i) + '"'

			_sql = 'select * from dmp.image where id in(' + _in_ + ')'
			self.parent.db_do_sql(_sql, update=True, need_clear=True)
			self.re_fill_enable = False
			self.can_repeat = True

	def set_data(self, data, need_clear=True):
		if data is not None:
			self.data = data
			self.fill_data(need_clear=need_clear)

	def on_first(self, event):
		if self.can_repeat is not None and self.can_repeat:
			self.parent.resume()
			self.can_repeat = False
