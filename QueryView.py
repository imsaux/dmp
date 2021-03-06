# encoding=utf-8
import wx
import wx.adv
import PopupControl
import wx.lib.masked as masked
import wx.lib.scrolledpanel as scrolled
import Util


class QueryView(scrolled.ScrolledPanel):
	def __init__(self, parent, query_items=None, nagetive=False):
		# wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.CLIP_CHILDREN)
		scrolled.ScrolledPanel.__init__(self, parent, -1)
		if query_items is None:
			return
		self.query_items = query_items
		self.is_nagetive = nagetive
		self.parent = parent
		self.ALL_SIZER = wx.BoxSizer(wx.VERTICAL)
		self.row = 1
		self.col = 0
		if self.is_nagetive:
			self.samples_amount = 0
		else:
			self.samples_amount = -1
		self.load()

	def load(self):
		checklist = []

		box_image_title = wx.StaticBox(self, -1, "图片")
		box_image = wx.StaticBoxSizer(box_image_title, wx.VERTICAL)
		grid_image = wx.FlexGridSizer(cols=3)
		self.image_ctrls = list()
		for item in self.query_items.keys():
			if self.query_items[item]['field'] not in ['id', 'path']:
				if self.query_items[item]['field'] == 'date':
					self.ctr_date_from = PopupControl.PopControl(self, 1, checklist, self, -1, pos=(30, 30))
					self.ctr_date_to = PopupControl.PopControl(self, 1, checklist, self, -1, pos=(30, 30))
					st = wx.StaticText(self, -1, ' ≤ 采集日期 ≤ ')
					self.image_ctrls.append((self.ctr_date_from, st, self.ctr_date_to))

					self.ctr_time_from = masked.Ctrl(self, -1, "",
					                                 autoformat='24HRTIMEHHMMSS',
					                                 demo=True,
					                                 name='24HRTIME')
					self.ctr_time_from.SetValue('00:00:00')
					self.ctr_time_to = masked.Ctrl(self, -1, "",
					                               autoformat='24HRTIMEHHMMSS',
					                               demo=True,
					                               name='24HRTIME')
					self.ctr_time_to.SetValue('23:59:59')
					st = wx.StaticText(self, -1, ' ≤ 采集时间 ≤ ')
					self.image_ctrls.append((self.ctr_time_from, st, self.ctr_time_to))

				elif self.query_items[item]['field'] in ['speed', 'scale', 'width', 'height']:  # 范围
					ctrl1 = wx.TextCtrl(self, -1, "", size=(120, -1))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_from', ctrl1)
					st = wx.StaticText(self, -1, ' ≤ ' + item + ' ≤ ')
					ctrl2 = wx.TextCtrl(self, -1, "", size=(120, -1))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_to', ctrl2)
					self.image_ctrls.append((ctrl1, st, ctrl2))

				elif self.query_items[item]['field'] in ['quality', 'line', 'side', 'site', 'weather', 'set', 'state']:
					st = wx.StaticText(self, -1, item)
					_sql = 'SELECT dmp.image.%s FROM dmp.image group by dmp.image.%s' % (
						self.query_items[item]['field'],
						self.query_items[item]['field'])
					_data = Util.execute_sql(_sql)
					_list = [str(x[0]) for x in _data]
					ctrl = PopupControl.PopControl(self, 2, _list, self, -1, pos=(30, 30))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_select', ctrl)
					self.image_ctrls.append((st, None, ctrl))

				elif self.query_items[item]['field'] in ['code']:
					dct = dict()
					_sql = 'SELECT distinct %s FROM dmp.image group by %s' % (
						self.query_items[item]['field'], self.query_items[item]['field'])
					_data = Util.execute_sql(_sql)
					_list = [str(x[0]) for x in _data]
					for c in _list:
						_kind = ''
						_type = ''
						if 'X' * 20 == c:
							continue
						if c[0] == 'J':
							_kind = c[1:4]
						elif c[0] == 'K':
							_type = c[1:4]
							_kind = c[4:6]
						elif c[0] == 'D':
							_type = 'D'
						elif c[0] == 'T' or c[0] == 'Q':
							_type = c[1]
							_kind = c[2:7]
						else:
							pass
						if c[0] not in dct.keys():
							dct[c[0]] = dict()

						if _type not in dct[c[0]].keys():
							dct[c[0]][_type] = list()

						dct[c[0]][_type].append(_kind)
					_types = [x for x in [list(dct[k1].keys()) for k1 in dct.keys()] if x != ['']]
					lt = list()
					for t in _types:
						lt.extend(t)
					_kinds = [x for x in [list(dct[k1].values()) for k1 in dct.keys()] if x != ['']]
					lk = list()
					for k in _kinds:
						for kk in k:
							lk.extend(kk)
					lk = list(set(lk))
					st = wx.StaticText(self, -1, '车属性')
					ctrl = PopupControl.PopControl(self, 2, list(dct.keys()), self, -1, pos=(30, 30))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_property', ctrl)
					self.image_ctrls.append((st, None, ctrl))

					st = wx.StaticText(self, -1, '车种')
					ctrl = PopupControl.PopControl(self, 2, lt, self, -1, pos=(30, 30))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_type', ctrl)
					self.image_ctrls.append((st, None, ctrl))

					st = wx.StaticText(self, -1, '车型')
					ctrl = PopupControl.PopControl(self, 2, lk, self, -1, pos=(30, 30))
					setattr(self, 'ctr' + '_' + self.query_items[item]['field'] + '_kind', ctrl)
					self.image_ctrls.append((st, None, ctrl))
				else:
					checklist.append(item)
		if len(checklist) > 0:
			st = wx.StaticText(self, -1, '其他')
			ctrl = PopupControl.PopControl(self, 2, checklist, self, -1, pos=(30, 30))
			setattr(self, 'ctr_other', ctrl)
			self.image_ctrls.append((st, None, ctrl))

		for item1, item2, item3 in self.image_ctrls:
			grid_image.Add(item1, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			if item2 is None:
				grid_image.Add(wx.StaticText(self, -1, ''), 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			else:
				grid_image.Add(item2, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			grid_image.Add(item3, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)

		box_image.Add(grid_image, 0, wx.LEFT | wx.ALL, 5)
		self.ALL_SIZER.Add(box_image, 0, wx.LEFT | wx.ALL, 5)

		box_label_title = wx.StaticBox(self, -1, "标签")
		box_label = wx.StaticBoxSizer(box_label_title, wx.VERTICAL)
		grid_label = wx.FlexGridSizer(cols=3)
		self.label_ctrls = []
		st = wx.StaticText(self, -1, '标签类型')
		ctrl = PopupControl.PopControl(self, 2, Util.label_type, self, -1, pos=(30, 30))
		# ctrl.SetValue(Util.label_type[0])
		setattr(self, 'ctr_label_type', ctrl)
		self.label_ctrls.append((st, None, ctrl))

		if not self.is_nagetive:
			st = wx.StaticText(self, -1, '包含检测项')
		else:
			st = wx.StaticText(self, -1, '不包含检测项')
		ctrl = PopupControl.PopControl(self, 2, list(Util.label_object.values()), self, -1, pos=(30, 30))
		setattr(self, 'ctr_label_object', ctrl)
		self.label_ctrls.append((st, None, ctrl))

		st = wx.StaticText(self, -1, '报警类型')
		ctrl = PopupControl.PopControl(self, 2, Util.alarm_type, self, -1, pos=(30, 30))
		setattr(self, 'ctr_alarm_type', ctrl)
		self.label_ctrls.append((st, None, ctrl))

		if self.is_nagetive:
			st = wx.StaticText(self, -1, '测试集比例')
			ctrl = wx.TextCtrl(self, -1)
			setattr(self, 'ctr_testset_input', ctrl)
			self.label_ctrls.append((st, None, ctrl))

			st = wx.StaticText(self, -1, '训练集比例')
			ctrl = wx.TextCtrl(self, -1)
			setattr(self, 'ctr_trainset_input', ctrl)
			self.label_ctrls.append((st, None, ctrl))

			st = wx.StaticText(self, -1, '样本数量')
			ctrl = wx.TextCtrl(self, -1)
			setattr(self, 'ctr_samples_input', ctrl)
			self.label_ctrls.append((st, None, ctrl))

		for item1, item2, item3 in self.label_ctrls:
			grid_label.Add(item1, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			if item2 is None:
				grid_label.Add(wx.StaticText(self, -1, ''), 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			else:
				grid_label.Add(item2, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)
			grid_label.Add(item3, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.TOP, 5)

		box_label.Add(grid_label, 0, wx.LEFT | wx.ALL, 5)
		self.ALL_SIZER.Add(box_label, 0, wx.LEFT | wx.ALL, 5)
		if not self.is_nagetive:
			_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
			self.btn_query = wx.Button(self, -1, '检索')
			self.btn_query.Bind(wx.EVT_BUTTON, self.on_query_click)
			# self.btn_clear = wx.Button(self, -1, '清空')
			# self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear_click)
			_line_sizer.Add(self.btn_query, 0, wx.ALIGN_CENTRE, 5)
			# _line_sizer.Add(self.btn_clear, 0, wx.ALIGN_CENTRE, 5)
			self.ALL_SIZER.Add(_line_sizer, 0, wx.ALIGN_CENTRE, 5)
		else:
			self.btn_query = wx.Button(self, -1, '确定')
			self.btn_query.Bind(wx.EVT_BUTTON, self.on_query_click)
			self.ALL_SIZER.Add(self.btn_query, 1, wx.ALIGN_CENTRE | wx.ALL, 5)
		self.SetSizer(self.ALL_SIZER)
		self.SetupScrolling()


	def on_clear_click(self, e):
		pass

	def on_query_click(self, event):
		self.label_object_value = None
		self.label_type_value = None
		self.parent.set_mode(1)
		if not self.is_nagetive:
			self.parent.clear_query_objects()
			self.parent.clear_dataview_data()
		base_sql = 'SELECT * FROM dmp.image where 1=1'
		for item in dir(self):
			if 'ctr_' in item:
				data = getattr(self, item).GetValue()
				if data == '':
					continue
				if 'date_from' in item:
					base_sql += ' AND LEFT(date_format(date, "%Y%m%d"), 8) >= ' + data
				elif 'date_to' in item:
					base_sql += ' AND LEFT(date_format(date, "%Y%m%d"), 8) <= ' + data
				elif 'time_from' in item:
					base_sql += ' AND LEFT(date_format(date, "%k%i%s"), 8) >= ' + ''.join(data.split(':'))
				elif 'time_to' in item:
					base_sql += ' AND LEFT(date_format(date, "%k%i%s"), 8) <= ' + ''.join(data.split(':'))
				elif 'ctr_other' == item:
					fields = [self.query_items[x]['field'] for x in data.split(',')]
					for field in fields:
						base_sql += ' AND ' + field + '=1'
				elif 'ctr_code_type' == item:
					base_sql += ' AND (0'
					for type in data.split(','):
						base_sql += ' OR code like "%' + type + '%"'
					base_sql += ')'
				elif 'ctr_code_property' == item:
					base_sql += ' AND (0'
					for type in data.split(','):
						base_sql += ' OR left(code, 1) = "' + type + '"'
					base_sql += ')'
				elif 'ctr_property_select' == item:
					base_sql += ' AND (0'
					for type in data.split(','):
						base_sql += ' OR left(code, 1) = "' + type + '"'
					base_sql += ')'
				elif 'ctr_code_kind' == item:
					base_sql += ' AND (0'
					for kind in data.split(','):
						base_sql += ' OR code like "%' + kind + '%"'
					base_sql += ')'
				elif 'ctr_label_type' == item:
					self.label_type_value = data
					# _in_ = ''
					# for i in data.split(','):
					# 	if _in_ == '':
					# 		_in_ += '"' + i + '"'
					# 	else:
					# 		_in_ += ',"' + i + '"'
					# base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.type in (' + _in_ + ')))'
				elif 'ctr_label_object' == item:
					self.label_object_value = data
					# _in_ = ''
					# for i in data.split(','):
					# 	if _in_ == '':
					# 		_in_ += '"' + i + '"'
					# 	else:
					# 		_in_ += ',"' + i + '"'
					# if not self.is_nagetive:
					# 	base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + _in_ + ')))'
					# else:
					# 	base_sql += ' AND id not in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + _in_ + ')))'
					# self.parent.set_query_objects(data)
				elif 'ctr_alarm_type' == item:
					_in_ = ''
					for i in data.split(','):
						if _in_ == '':
							_in_ += '"' + i + '"'
						else:
							_in_ += ',"' + i + '"'
					base_sql += ' AND id in (SELECT ria.image_id FROM dmp.r_image_alarm as ria WHERE ria.alarm_id in (SELECT a.id FROM dmp.alarm as a WHERE a.name in (' + _in_ + ')))'
				elif 'ctr_testset_input' == item:
					try:
						self.test_set_percent = float(data)
					except Exception as e:
						self.test_set_percent = 0
				elif 'ctr_trainset_input' == item:
					try:
						self.train_set_percent = float(data)
					except Exception as e:
						self.train_set_percent = 0
				elif 'ctr_samples_input' == item:
					try:
						self.samples_amount = int(data)
					except Exception as e:
						self.samples_amount = 0
				else:
					fields = item.split('_')
					_field = None
					if len(fields) == 3:
						_field = fields[1]
					elif len(fields) == 4:
						_field = '_'.join([fields[1], fields[2]])

					if '_from' in item:
						base_sql += ' AND ' + _field + ' >= ' + data
					elif '_to' in item:
						base_sql += ' AND ' + _field + ' <= ' + data
					elif '_select' in item:
						_in_ = ''
						for i in data.split(','):
							if _in_ == '':
								_in_ += '"' + i + '"'
							else:
								_in_ += ',"' + i + '"'

						base_sql += ' AND ' + _field + ' in (' + _in_ + ')'

		if self.label_type_value is not None:
			if not self.is_nagetive:
				base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.type in (' + ','.join(['"'+str(x)+'"' for x in self.label_type_value.split(',')]) + ')))'
			else:
				base_sql += ' AND id not in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.type in (' + ','.join(['"'+str(x)+'"' for x in self.label_type_value.split(',')]) + ')))'

		if self.label_object_value is not None:
			_tmp = []
			for obj in self.label_object_value.split(','):
				if self.label_type_value is None:
					_tmp.append(obj + '-' + '分类')
					_tmp.append(obj + '-' + '目标检测')
					_tmp.append(obj + '-' + '分割')
				else:
					for typ in self.label_type_value.split(','):
						_tmp.append(obj + '-' + typ)
			if not self.is_nagetive:
				base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + ','.join(['"'+str(x)+'"' for x in self.label_object_value.split(',')]) + ')))'
			else:
				base_sql += ' AND id not in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + ','.join(['"'+str(x)+'"' for x in self.label_object_value.split(',')]) + ')))'
			self.parent.set_query_objects(_tmp)

		#
		# if self.label_object_value is not None and self.label_type_value is not None:
		# 	_tmp = []
		# 	for obj in self.label_object_value.split(','):
		# 		for typ in self.label_type_value.split(','):
		# 			_tmp.append(obj + '-' + typ)
		#
		# 	if not self.is_nagetive:
		# 		base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + ','.join(['"'+str(x)+'"' for x in self.label_object_value.split(',')]) + ') and l.type in (' + ','.join(['"'+str(x)+'"' for x in self.label_type_value.split(',')]) + ')))'
		# 	else:
		# 		base_sql += ' AND id not in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + ','.join(['"'+str(x)+'"' for x in self.label_object_value.split(',')]) + ') and l.type in (' + ','.join(['"'+str(x)+'"' for x in self.label_type_value.split(',')]) + ')))'
		# 	self.parent.set_query_objects(_tmp)
		#
		try:
			self.parent.last_data_set = set()
			if self.is_nagetive:
				self.parent.db_do_sql(base_sql, update=True, need_clear=True, need_random=self.samples_amount, need_last=True, for_dataview=True)
			else:
				self.parent.db_do_sql(base_sql, update=True, need_clear=False if self.is_nagetive else True, need_last=True, for_dataview=True)
			self.parent.on_show_data_view()
		except Exception as e:
			Util.LOG.error(repr(e))
		finally:
			self.samples_amount = -1

