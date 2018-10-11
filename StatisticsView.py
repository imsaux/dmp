# encoding=utf-8
import wx
import wx.dataview as dv
import Util


class StatisticsView(wx.Panel):
	def __init__(self, parent, data=None, mode=None):
		wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		self.data = data
		self.mode = mode
		self._all_data = []
		self.re_fill_enable = True
		self.can_repeat = None
		self.dvc = dv.DataViewListCtrl(
			self,
			style=wx.BORDER_THEME | dv.DV_ROW_LINES  | dv.DV_VERT_RULES | dv.DV_MULTIPLE)

		self.dvc.AppendTextColumn('检测项', width=100)
		self.dvc.AppendTextColumn('原图', width=100)
		self.dvc.AppendTextColumn('负样本', width=100)
		self.dvc.AppendTextColumn('补充素材', width=100)
		if self.data is not None:
			self.fill_data()
		else:
			self.dvc.AppendItem(('合计', '0', '0', '0'))
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(self.dvc, 1, wx.EXPAND)

		# b2 = wx.Button(self, label="恢复", name="first")
		# self.Bind(wx.EVT_BUTTON, self.on_first, b2)

		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		# btnbox.Add(b2, 0, wx.LEFT | wx.RIGHT, 5)
		self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
		self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_refill_data)

	def get_objects(self, data, add=False):
		if not add:
			self._all_data = list()
		for id in [x[0] for x in data]:
			_sql = "SELECT (select concat(l.name,'-', l.type) from dmp.label l where id=ril.label_id), count(label_id), image_id FROM dmp.r_image_label ril where image_id=%s group by label_id, image_id;"
			_data = Util.execute_sql(_sql, args=(id,))
			self._all_data.append(_data)

	def fill_data(self, mode=0, refresh=False, need_clear=True):
		if need_clear:
			self.clear_data()
		if mode == 0:
			self.get_objects(self.data)
		elif mode == 1:
			self._all_data = self.data
		if refresh:
			_in_ = ''
			for i in [x[0] for x in self.data]:
				if _in_ == '':
					_in_ += '"' + str(i) + '"'
				else:
					_in_ += ',"' + str(i) + '"'

			_sql = 'select * from dmp.image where id in(%s)'
			self.parent.db_do_sql(_sql, args=(_in_,), update=True)
		else:
			self.sum_result(self._all_data, mode=mode)
		self.re_fill_enable = True
	
	def get_data(self, is_data=True):
		if is_data:
			return self.data
		else:
			rows = self.dvc.ItemCount
			_return = list()
			for r in range(rows):
				_return.append((self.dvc.GetValue(r, 0), self.dvc.GetValue(r, 1)))
			return _return

	def to_dict(self):
		data = dict()
		for i in range(self.dvc.ItemCount):
			_key = self.dvc.GetValue(i, 0)
			if _key != '合计':
				data[_key] = [
					self.dvc.GetValue(i, 1),
					self.dvc.GetValue(i, 2),
					self.dvc.GetValue(i, 3),
				]
		return data

	def from_dict(self, d, sum_negative=0):
		if len(d) == 0:
			return
		self.dvc.DeleteAllItems()
		for _key in d.keys():
			try:
				self.dvc.AppendItem((_key, str(d[_key][0]), str(d[_key][1]), str(d[_key][2])))
			except Exception as e:
				pass
		_sum_origin = sum([x[0] for x in d.values()]) if len(d) > 0 else 0
		_sum_negative = sum_negative
		_sum_replenish = sum([x[2] for x in d.values()]) if len(d) > 0 else 0
		self.dvc.AppendItem(('合计', str(_sum_origin), str(_sum_negative), str(_sum_replenish)))

	def sum_result(self, data, mode=0):
		_sum_ = dict()
		sum_negative = 0
		data_view = self.to_dict()
		if mode == 1:
			sum_negative = len(data)
		else:
			for item in data:
				if item is None:
					continue
				if len(item) > 0:
					for i in item:
						if '-' in i[0]:
							if i[0] not in _sum_.keys():
								_sum_[i[0]] = [0, 0, 0]
							_sum_[i[0]][mode] += i[1]
			data_view.update(_sum_)
		self.from_dict(data_view, sum_negative=sum_negative)

	def on_refill_data(self, event):
		# item = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 0)
		# if item != '素材数量':
		# 	if self.re_fill_enable:
		# 		self.re_fill_data(item)
		pass

	def clear_data(self):
		self.dvc.DeleteAllItems()

	def re_fill_data(self, item, need_clear=True):
		if need_clear:
			self.clear_data()
		items = []
		ids = []
		self.get_objects(self.parent.last_data, add=True)
		l = [x for x in self._all_data if x is not None and len(x) > 0]
		for x in l:
			for y in x:
				if y[0] == item:
					items.append(x)
					ids.append(y[2])
		_in_ = ''
		if len(ids) > 0:
			for i in ids:
				if _in_ == '':
					_in_ += '"' + str(i) + '"'
				else:
					_in_ += ',"' + str(i) + '"'

			_sql = 'select * from dmp.image where id in(' + _in_ + ')'
			self.parent.db_do_sql(_sql, update=True, need_clear=True, )
			self.re_fill_enable = False
			self.can_repeat = True
		self.sum_result(items, show_negative=False)

	def set_data(self, data, mode=0, need_clear=True):
		if data is not None:
			self.data = data
			self.fill_data(need_clear=need_clear, mode=mode)

	def on_first(self, event):
		if self.can_repeat is not None and self.can_repeat:
			self.parent.resume()
			self.can_repeat = False
