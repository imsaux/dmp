# encoding=utf-8
"""
1. 检索
2. 补充素材（图像处理）
3. 导出 （设置尺度）
4. 缩放并裁剪生成图片及相应标签
"""
import datetime
import os.path
import wx
import wx.dataview as dv
import Wizard
import add_nagetive
import add_replenish

ID_MODE_IMPORT = 0
ID_MODE_EXPORT = 1


class DataView(wx.Panel):
	def __init__(self, parent, log, data=None, mode=ID_MODE_IMPORT):
		wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		self.data = data
		self.mode = mode
		self.log = log
		self.id = -1
		self.edit_items = list()
		self._replenish_data = None
		self.last_edit_row = -1
		self.last_edit_col = -1
		self.dvc = dv.DataViewListCtrl(self,
		                               style=wx.BORDER_THEME
		                                     | dv.DV_ROW_LINES  # nice alternating bg colors
		                                     | dv.DV_VERT_RULES
		                                     | dv.DV_MULTIPLE
		                               )

		self.dvc_init()
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(self.dvc, 1, wx.EXPAND)

		# b1 = wx.Button(self, label="保存", name="save")
		# self.Bind(wx.EVT_BUTTON, self.on_save, b1)
		b1 = wx.Button(self, label="清空", name="save")
		self.Bind(wx.EVT_BUTTON, self.on_clear, b1)
		b2 = wx.Button(self, label="导入", name="import")
		self.Bind(wx.EVT_BUTTON, self.on_import, b2)
		b3 = wx.Button(self, label="导出", name="export")
		self.Bind(wx.EVT_BUTTON, self.on_export, b3)
		b4 = wx.Button(self, label="添加负样本", name="nagetive")
		self.Bind(wx.EVT_BUTTON, self.on_add_negative, b4)
		b5 = wx.Button(self, label="补充素材", name="replenish")
		self.Bind(wx.EVT_BUTTON, self.on_add_replenish, b5)

		btnbox = wx.BoxSizer(wx.HORIZONTAL)
		# btnbox.Add(b1, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b1, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b2, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b3, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b4, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b5, 0, wx.LEFT | wx.RIGHT, 5)
		self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
		self.bind_event()
		if self.data is not None:
			self.set_data(self.data)

	def bind_event(self):
		self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_dbclick)
		# self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.on_edit_done)
		# self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_STARTED, self.on_edit_start)
		# self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_popup_menu)

	def on_nagetive(self, e):
		if self.dvc.ItemCount > 0 and self.parent.mode == ID_MODE_EXPORT:
			an = add_nagetive.NagetiveAddFrame(self.parent)

	def on_clear(self, e):
		self.clear_data()

	def on_popup_menu(self, e):
		try:
			if e.EventObject.SelectedRow != -1:
				self.id = self.dvc.GetValue(e.EventObject.SelectedRow, 1)
				m_dataview = wx.Menu()
				item2 = wx.MenuItem(m_dataview, wx.NewId(), "补充素材")
				self.Bind(wx.EVT_MENU, self.on_add_replenish, item2)
				m_dataview.Append(item2)
				self.PopupMenu(m_dataview)
		except Exception as e:
			pass

	def on_add_negative(self, e):  # 添加负样本
		if self.dvc.ItemCount > 0 and self.parent.mode == ID_MODE_EXPORT:
			an = add_nagetive.NagetiveAddFrame(self.parent)

	def on_add_replenish(self, e):  # 添加补充素材
		if self.dvc.ItemCount > 0:
			ids = [self.dvc.GetValue(r, 1) for r in range(self.dvc.ItemCount) if self.dvc.GetValue(r, 0)]
			f = wx.Frame(None, -1, '添加补充素材')
			f.SetSize((500, 400))
			ar = add_replenish.ReplenishAdd(f, self.log, main_view_obj=self.parent, objects=self.parent.last_query_objects, ids=ids, statistics_data=self.parent.statistics_panel.get_data(is_data=False), data_view_obj=self)
			f.Show()

	def on_item_dbclick(self, event):
		if self.mode == 1:
			_id = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 1)
			_sql = 'select path from dmp.image where id=' + _id
			img = self.parent.db_do_sql(_sql)[0][0]
			if os.path.exists(img):
				self.parent.image_panel.set_image(img)
				self.parent.on_show_image_view()
		if self.mode == 0:
			_path = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 2)
			if os.path.exists(_path):
				self.parent.image_panel.set_image(_path)
				self.parent.on_show_image_view()

	def on_import(self, evt):
		if self.parent.mode == 0 and self.dvc.GetItemCount() > 0:
			rows = self.dvc.GetItemCount()
			cols = self.dvc.GetColumnCount()
			if rows > 0:
				all = list()
				for i in range(rows):
					files = list()
					for j in range(cols):
						if j > 1 and self.dvc.GetValue(i, 0):
							files.append(self.dvc.GetValue(i, j))
					all.append(files)
				for l in all:
					if len(l) > 0:
						_insert_image_sql = 'insert into dmp.image (dmp.image.path, dmp.image.code, dmp.image.side, dmp.image.datetime, dmp.image.line, dmp.image.site, dmp.image.width, dmp.image.height, dmp.image.speed, dmp.image.scale, dmp.image.set_type, dmp.image.status, dmp.image.last, dmp.image.tarpaulin, dmp.image.range, dmp.image.weather, dmp.image.quality_level, dmp.image.calibration_info, dmp.image.axel_info, dmp.image.valid) values ("", "' + l[1] + '", "' + l[2] + '","' + datetime.datetime.strptime(l[3],'%Y%m%d%H%M%S').strftime("%Y-%m-%d %H:%M:%S") + '","' + l[4] + '","' + l[5] + '",' + str(l[6]) + ',' + str(l[7]) + ',' + str(l[8]) + ',' + str(l[9]) + ',"' + l[10] + '","' + l[11] + '",' + str(l[12]) + ',' + str(l[13]) + ',' + str(l[14]) + ',"' + str(l[15]) + '",' + str(l[16]) + ',' + str(l[17]) + ',' + str(l[18]) + ',' + str(l[19]) + ');'
						self.parent.db_do_sql(_insert_image_sql, need_commit=True)
						_select_image_sql = 'select id from dmp.image where dmp.image.code="' + l[1] + '" and dmp.image.datetime="' + datetime.datetime.strptime(l[3],'%Y%m%d%H%M%S').strftime("%Y-%m-%d %H:%M:%S") + '" and dmp.image.width=' + str(l[6]) + ' and dmp.image.height=' + str(l[7]) + ' and dmp.image.speed=' + str(l[8]) + ' and dmp.image.line="' + l[4] + '"'
						_id = self.parent.db_do_sql(_select_image_sql)[0][0]
						# todo 向服务器发送文件
		else:
			r = Wizard.show_import_wizard(self)
			if r is not None:
				self.parent.set_import_param(r)
	
	def gen_export_works(self, ids, exparams):
		work = list()
		for _id in ids:
			work.append((
				_id, 
				exparams['need_cutting'],
				exparams['need_zoom'],
				exparams['scale'],
				exparams['export_path'],
				self._replenish_data[_id] if self._replenish_data is not None and _id in self._replenish_data.keys() else dict()
				))
		return work

			

	def on_export(self, evt):
		if self.parent.mode == 1 and self.dvc.GetItemCount() > 0:
			r = Wizard.show_export_wizard(self)
			row = self.dvc.GetItemCount()
			ids = [self.dvc.GetValue(r, 1) for r in range(row) if self.dvc.GetValue(r, 0)]
			if r is not None and len(ids) > 0:
				self.parent.to_export(self.gen_export_works(ids, r))
		elif self.dvc.GetItemCount() == 0:
			wx.MessageBox('请先检索数据！')
		else:
			pass

	def dvc_init(self):
		i = 0
		self.dvc.AppendToggleColumn('选择', width=30, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
		for key in self.parent.db_column_info.keys():
			# i += 1
			# if i < 14:
			# 	self.dvc.AppendTextColumn(key, width=100)
			# else:
			# 	self.dvc.AppendTextColumn(key, width=100, mode=dv.DATAVIEW_CELL_EDITABLE) # 可编辑
			self.dvc.AppendTextColumn(key, width=60)
		self.dvc.AppendTextColumn('类型', width=40)
		for c in self.dvc.Columns:
			c.Sortable = True

	def clear_data(self):
		self.dvc.DeleteAllItems()
		self.parent.clear_statisticspanel_data()

	def set_replenish_data(self, data): # 设置补充操作对象
		self._replenish_data = data 

	def set_data(self, data, need_clear=True):
		if data is not None:
			self.data = data
			if need_clear:
				self.clear_data()
			try:
				for line in self.data:
					_data = list()
					for x in [True] + list(line):
						if isinstance(x, datetime.datetime):
							_data.append(x.strftime("%Y%m%d%H%M%S"))
						elif x in [True, False]:
							_data.append(x)
						elif isinstance(x, int):
							_data.append(x)
						elif isinstance(x, str):
							_data.append(x)
						else:
							_data.append(repr(x))

					self.dvc.AppendItem(_data)
			except Exception as e:
				self.parent.log.info(repr(e))




	# def on_save(self, evt):
	# 	if len(self.edit_items) > 0:
	# 		for update in self.edit_items:
	# 			_sql = 'update dmp.image set image.' + update[0] + ' = ' + str(update[1]) + ' where id=' + str(
	# 				update[2])
	# 			self.parent.db_do_sql(_sql, need_commit=True)
	# 		self.edit_items = list()

	# def on_edit_done(self, event):
	# 	field = self.parent.db_column_info[self.dvc.GetColumn(self.last_edit_col).GetTitle()]['field']
	# 	try:
	# 		if self.parent.db_column_info[event.EventObject.GetCurrentColumn().GetTitle()]['type'] == 'int':
	# 			_new_value = int(event.GetValue())
	# 		elif self.parent.db_column_info[event.EventObject.GetCurrentColumn().GetTitle()]['type'] == 'varchar':
	# 			_new_value = str(event.GetValue())
	# 		image_id = self.dvc.GetValue(self.last_edit_row, 1)
	# 		self.edit_items.append((field, _new_value, image_id))
	# 	except Exception as e:
	# 		self.parent.log.info(repr(e))
	# 	finally:
	# 		self.last_edit_row = -1
	# 		self.last_edit_col = -1

	# def on_edit_start(self, event):
	# 	self.last_edit_row = event.EventObject.SelectedRow
	# 	self.last_edit_col = event.EventObject.GetColumnPosition(event.EventObject.GetCurrentColumn())

