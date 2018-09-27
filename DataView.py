# encoding=utf-8
"""
1. 检索
2. 补充素材（图像处理）
3. 导出 （设置尺度）
4. 缩放并裁剪生成图片及相应标签
"""
import Util
import datetime
import os.path
import wx
import wx.dataview as dv
import Wizard
import Add_nagetive
import Add_replenish
import CarClassification
import PIL.Image
from threading import Thread, Lock
import pubsub.pub
import concurrent.futures
import Client
import Cutting
import inspect

ID_MODE_IMPORT = 0
ID_MODE_EXPORT = 1

mutex = Lock()


class UI_thread(Thread):
	def __init__(self, mode, args, p=None, objs=None):
		Thread.__init__(self)
		self.mode = mode
		self.args = args
		self.query_objs = objs
		self.p = p
		self.start()

	def run(self):
		if self.mode == 0:
			self.to_import(self.args)
		elif self.mode == 1:
			self.to_export(self.args)
		wx.CallAfter(pubsub.pub.sendMessage, 'over', msg='over')

	def e_to_send(self, work):
		c = Client.Client(Util.HOST, Util.PORT)
		c.put_data(work[0], work[1][0])
		if len(work[2]) > 0:
			for _type in work[2].keys():
				if work[2]['type'] == 'S':
					_type = '分割'
				else:
					return work[1][0]
				for _data in work[2][_type]:
					_get_path_sql = 'select dmp.r_image_label.id, dmp.r_image_label.data from dmp.r_image_label where dmp.r_image_label.image_id=%s and dmp.r_image_label.label_id=(select dmp.label.id from dmp.label where dmp.label.type=%s and dmp.label.name=%s)'
					_result = Util.execute_sql(_get_path_sql, args=(work[1][0], _type, Util.label_object[_data[0]]))[0]
					c.put_data(_result[1], _result[0], 1)
		wx.CallAfter(pubsub.pub.sendMessage, 'import', msg=str(work[0]))
		return work[1][0]

	def to_import(self, works):  # 导入流程
		work_result = list()
		with concurrent.futures.ThreadPoolExecutor() as executor:
			fs = {executor.submit(self.e_to_send, w): w for w in works[0]}
			for future in concurrent.futures.as_completed(fs):
				try:
					work_result.append(future.result())
				except Exception as e:
					Util.LOG.error(repr(e))

	def e_to_recv(self, work):
		c = Client.Client(Util.HOST, Util.PORT)
		c.get_data(work[0], work[4])
		wx.CallAfter(pubsub.pub.sendMessage, 'export', mode='recv', msg=str(work[0]))
		return work[0]

	def to_export(self, works):  # 导出流程
		work_result = list()

		# 传输
		with concurrent.futures.ThreadPoolExecutor() as executor:
			fs = {executor.submit(self.e_to_recv, w): w for w in works[0]}
			for future in concurrent.futures.wait(fs, return_when=concurrent.futures.ALL_COMPLETED):
				try:
					work_result.append(future.result())
				except Exception as e:
					Util.LOG.error(repr(e))
					Util.LOG.debug(repr(works))

		# with concurrent.futures.ThreadPoolExecutor() as executor:
		# 	fs = {executor.submit(self.e_to_cutting, w): w for w in works}
		# 	for future in concurrent.futures.wait(fs, return_when=concurrent.futures.ALL_COMPLETED):
		# 		try:
		# 			work_result.append(future.result())
		# 		except Exception as e:
		# 			Util.LOG.error(repr(e))
		# 			Util.LOG.debug(repr(works))

	def e_to_process(self, work):  # 图像处理
		return work

	def e_to_zoom(self, work):  # 缩放
		return work

	def e_to_cutting(self, work):  # 裁剪
		# work -> 图像地址
		if isinstance(self.query_objs, set) and len(self.query_objs) > 0:
			_methods = []
			for obj in [obj.split('-')[0] for obj in self.query_objs]:
				if obj in Util.cutting_relation['object'].keys():
					_methods.append(Util.cutting_relation['object'][obj])
			_tmp = []
			[_tmp.extend(x) for x in _methods]
			_methods = set(_tmp)
			if len(_methods) == 1:  # 进行裁剪
				for r, d, f in os.walk(Util.CUTTING_DIR):
					for _file in f:
						os.remove(_file)
					break
				_all_ = inspect.getmembers(Cutting)
				_cls = [i[1] for i in _all_ if i[0] == list(_methods)[0]][0]
				_t = _cls(work, Util.CUTTING_DIR)
				_t.cut()
				wx.CallAfter(pubsub.pub.sendMessage, 'export', mode='cutting', msg=str(work))
			return work, True
		return work, False


class DataView(wx.Panel):
	def __init__(self, parent, data=None, mode=ID_MODE_IMPORT):
		wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		self.data = data
		self.mode = mode
		self.info = {
			'import': {
				'send': [],
				'_send': 0
			},
			'export': {
				'cutting': [],
				'process': [],
				'zoom': [],
				'recv': [],
				'_cutting': 0,
				'_process': 0,
				'_zoom': 0,
				'_recv': 0
			}
		}
		self.id = -1
		self.edit_items = list()
		self.import_data = dict()
		self._replenish_data = None
		self.last_edit_row = -1
		self.last_edit_col = -1
		self.dvc = dv.DataViewListCtrl(self, style=wx.BORDER_THEME | dv.DV_ROW_LINES | dv.DV_VERT_RULES | dv.DV_MULTIPLE)

		self.dvc_init()
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(self.dvc, 1, wx.EXPAND)

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
		btnbox.Add(b1, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b2, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b3, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b4, 0, wx.LEFT | wx.RIGHT, 5)
		btnbox.Add(b5, 0, wx.LEFT | wx.RIGHT, 5)
		self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
		self.bind_event()
		if self.data is not None:
			self.set_data(self.data)
		pubsub.pub.subscribe(self.update_export, 'export')
		pubsub.pub.subscribe(self.update_import, 'import')
		pubsub.pub.subscribe(self.over_evt_handler, 'over')

	def over_evt_handler(self, msg):
		self.parent.reload()

	def update_export(self, mode, msg):
		self.info['export'][mode].append(msg)
		comment = ''
		if mode == 'recv':
			comment = '已传输：'
		elif mode == 'cutting':
			comment = '已裁剪：'
		elif mode == 'process':
			comment = '已处理：'
		self.parent.statusbar.SetStatusText('导出操作 ' + comment + str(len(self.info['export'][mode])), 1)

	def update_import(self, msg):
		self.info['import']['send'].append(msg)
		self.parent.statusbar.SetStatusText('导入操作 ' + '已传输：' + str(len(self.info['import']['send'])), 0)


	def bind_event(self):
		self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_dbclick)

	def on_nagetive(self, e):
		if self.dvc.ItemCount > 0 and self.mode == ID_MODE_EXPORT:
			an = Add_nagetive.NagetiveAddFrame(self.parent)

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
		if self.dvc.ItemCount > 0 and self.mode == ID_MODE_EXPORT:
			an = Add_nagetive.NagetiveAddFrame(self.parent)

	def on_add_replenish(self, e):  # 添加补充素材
		if self.dvc.ItemCount > 0:
			ids = [self.dvc.GetValue(r, 1) for r in range(self.dvc.ItemCount) if self.dvc.GetValue(r, 0)]
			f = wx.Frame(None, -1, '添加补充素材')
			f.SetSize((500, 400))
			ar = Add_replenish.ReplenishAdd(f, objects=self.parent.last_query_objects, ids=ids,
			                                statistics_view_obj=self.parent.statistics_panel, data_view_obj=self,
			                                last_data=self._replenish_data)
			f.Show()

	def on_item_dbclick(self, event):
		if self.mode == ID_MODE_EXPORT:
			_id = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 1)
			_sql = 'select path from dmp.image where id=' + _id
			img = Util.execute_sql(_sql)[0][0]
			if os.path.exists(img):
				self.parent.image_panel.set_image(img)
				self.parent.on_show_image_view()
			else:
				c = Client.Client(Util.HOST, Util.PORT)
				c.get_data(int(_id), Util.ORIGIN_DIR)
				_img = os.path.join(Util.ORIGIN_DIR, os.path.basename(img))
				if os.path.exists(_img):
					self.parent.image_panel.set_image(_img)
					self.parent.on_show_image_view()
		if self.mode == ID_MODE_IMPORT:
			_path = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 2)
			if os.path.exists(_path):
				self.parent.image_panel.set_image(_path)
				self.parent.on_show_image_view()

	def on_import(self, evt):
		if self.mode == ID_MODE_IMPORT and self.dvc.GetItemCount() > 0:
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
				work_ids = list()
				with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
					fs = {executor.submit(self.thread_insert_to_image, l): l for l in all if len(l) > 0}
					for future in concurrent.futures.as_completed(fs):
						try:
							work_ids.append(future.result())
						except Exception as e:
							Util.LOG.error(repr(e))
				with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
					fs = {executor.submit(self.thread_insert_to_r_image_label, key): key for key in
					      self.import_data.keys()}
					for future in concurrent.futures.as_completed(fs):
						pass
				# self.parent.to_import(self.gen_import_works(work_ids))
				self.info = {
					'import': {
						'send': [],
						'_send': 0
					},
					'export': {
						'cutting': [],
						'process': [],
						'zoom': [],
						'recv': [],
						'_cutting': 0,
						'_process': 0,
						'_zoom': 0,
						'_recv': 0
					}
				}
				UI_thread(self.mode, (self.gen_import_works(work_ids),),p=self.parent)
				# btn = evt.GetEventObject()
				# btn.Disable()
		else:
			r = Wizard.show_import_wizard(self)
			if r is None:
				return
			if 'image' in r.keys():
				c = CarClassification.CarClassification(r['image']).IndexData
				index = 1
				all_data = list()
				for _root, _dir, _file in os.walk(r['image']):
					for f in _file:
						if os.path.splitext(f)[1].upper() == '.JPG':
							_key = os.path.join(_root, f)
							if _key not in self.import_data.keys():
								self.import_data[_key] = dict()

							tmp_root = _root.split('\\')
							tmp_file = f.split('_')[-1].split('.')[0]
							try:
								img_path = os.path.join(_root, f)
								img = PIL.Image.open(img_path)

								data = [
									index,
									os.path.join(_root, f),
									c[tmp_root[-2]][tmp_root[-1]][tmp_file]['code'],
									f.split('_')[-3],
									f.split('_')[-2][0],
									f.split('_')[-4],
									r['site'],
									img.width,
									img.height,
									c[tmp_root[-2]][tmp_root[-1]][tmp_file]['speed'],
									1.0,
									0,
									0,
									'晴',
									0,
									0,
									0,
									0,
									'未标',
									'无',
									'原图'
								]
								all_data.append(data)
								index += 1
							except Exception as e:
								Util.LOG.error(repr(e))
				self.set_data(all_data)
			else:
				index = 1
				show_data = list()
				for _root, _dir, _file in os.walk(r['label_dir'], topdown=False):
					if r['label_type'] == '分割标签':
						if 'image' == _root.split('\\')[-1]:
							for f in _file:
								if os.path.splitext(f)[1].upper() == '.JPG':
									_key = os.path.join(_root, f)
									if _key not in self.import_data.keys():
										self.import_data[_key] = dict()

									img_path = os.path.join(_root, f)
									img = PIL.Image.open(img_path)

									data = [
										index,
										os.path.join(_root, f),
										self.get_type_by_kind(r['car_kind']),
										Util._datetime_format(mode=2),
										'L',
										'202.202.202.2',
										'杨柳青',
										img.width,
										img.height,
										900,
										float(r['image_scale']),
										0,
										0,
										'晴',
										0,
										0,
										0,
										0,
										'未标',
										'测试',
										'原图'
									]
									show_data.append(data)
									index += 1
						if 'Glabel' == _root.split('\\')[-1]:
							for f in _file:

								_label_data = list()
								_key = '\\'.join(
									os.path.join(_root, f).split('\\')[:-2]) + '\\' + 'image' + '\\' + '.'.join(
									os.path.basename(f).split('.')[:-1]) + '.jpg'
								if _key not in self.import_data.keys():
									self.import_data[_key] = dict()
								_label_data.append((r['label_obj'], os.path.join(_root, f)))
								if 'S' not in self.import_data[_key].keys():
									self.import_data[_key]['S'] = list()
								self.import_data[_key]['S'] = _label_data
					elif r['label_type'] == '分类标签':
						for f in _file:
							if os.path.splitext(f)[1].upper() != '.JPG':
								continue
							_key = os.path.join(_root, f)
							if _key not in self.import_data.keys():
								self.import_data[_key] = dict()
							img_path = os.path.join(_root, f)
							img = PIL.Image.open(img_path)
							data = [
								index,
								os.path.join(_root, f),
								self.get_type_by_kind(r['car_kind']),
								Util._datetime_format(mode=2),
								'L',
								'202.202.202.2',
								'杨柳青',
								img.width,
								img.height,
								900,
								float(r['image_scale']),
								0,
								0,
								'晴',
								0,
								0,
								0,
								0,
								'未标',
								'训练',
								'原图'
							]
							show_data.append(data)
							index += 1
							_label_data = list()
							if 'positive' in _root:
								_tmp = '%s 0.0 0 0.0 %s %s %s %s 0.0 0.0 0.0 0.0 0.0 0.0 0.0' % (
								r['label_obj'], '0', '0', str(img.width), str(img.height))
								_label_data.append((r['label_obj'], _tmp))

							if 'negative' in _root:
								_label_data.append((r['label_obj'], ''))
							if 'C' not in self.import_data[_key].keys():
								self.import_data[_key]['C'] = list()
							self.import_data[_key]['C'] = _label_data
					elif r['label_type'] == '目标检测标签':
						if 'image' == _root.split('\\')[-1] and 'train' == _root.split('\\')[-2]:
							for f in _file:
								if os.path.splitext(f)[1].upper() == '.JPG':
									_key = os.path.join(_root, f)
									if _key not in self.import_data.keys():
										self.import_data[_key] = dict()
									img_path = os.path.join(_root, f)
									img = PIL.Image.open(img_path)

									data = [
										index,
										os.path.join(_root, f),
										self.get_type_by_kind(r['car_kind']),
										Util._datetime_format(mode=2),
										'L',
										'202.202.202.2',
										'杨柳青',
										img.width,
										img.height,
										900,
										float(r['image_scale']),
										0,
										0,
										'晴',
										0,
										0,
										0,
										0,
										'未标',
										'训练',
										'原图'
									]
									show_data.append(data)
									index += 1
						if 'image' == _root.split('\\')[-1] and 'val' == _root.split('\\')[-2]:
							for f in _file:
								if os.path.splitext(f)[1].upper() == '.JPG':
									_key = os.path.join(_root, f)
									if _key not in self.import_data.keys():
										self.import_data[_key] = dict()

									img_path = os.path.join(_root, f)
									img = PIL.Image.open(img_path)

									data = [
										index,
										os.path.join(_root, f),
										self.get_type_by_kind(r['car_kind']),
										Util._datetime_format(mode=2),
										'L',
										'202.202.202.2',
										'杨柳青',
										img.width,
										img.height,
										900,
										float(r['image_scale']),
										0,
										0,
										'晴',
										0,
										0,
										0,
										0,
										'未标',
										'测试',
										'原图'
									]
									show_data.append(data)
									index += 1
						if 'Blabel' == _root.split('\\')[-1]:
							for f in _file:
								if os.path.splitext(f)[1].upper() == '.TXT':
									_key = '\\'.join(
										os.path.join(_root, f).split('\\')[:-2]) + '\\' + 'image' + '\\' + '.'.join(
										os.path.basename(f).split('.')[:-1]) + '.jpg'

									if _key not in self.import_data.keys():
										self.import_data[_key] = dict()
									_label_data = list()
									with open(os.path.join(_root, f), 'r') as fr:
										while True:
											_line = fr.readline()
											_type = _line.split(' ')[0]
											_new_type = self.get_new_type(_root, _type)
											if _new_type != '':
												_label_data.append((_new_type, _line.replace(_type, _new_type)))
											if not _line:
												break
									if 'D' not in self.import_data[_key].keys():
										self.import_data[_key]['D'] = list()
									self.import_data[_key]['D'] = _label_data
					else:
						for f in _file:
							if os.path.splitext(f)[1].upper() == '.JPG':
								_key = os.path.join(_root, f)
								if _key not in self.import_data.keys():
									self.import_data[_key] = dict()
								img_path = os.path.join(_root, f)
								img = PIL.Image.open(img_path)

								data = [
									index,
									os.path.join(_root, f),
									self.get_type_by_kind(r['car_kind']),
									Util._datetime_format(mode=2),
									'L',
									'202.202.202.2',
									'杨柳青',
									img.width,
									img.height,
									900,
									float(r['image_scale']),
									0,
									0,
									'晴',
									0,
									0,
									0,
									0,
									'未标',
									'训练',
									'原图'
								]
								show_data.append(data)
								index += 1

					self.set_data(show_data)
			self.mode = ID_MODE_IMPORT

	def get_type_by_kind(self, kind):
		if kind == '客车':
			return 'KTT01T 100000 A000  '
		elif kind == '敞车':
			return 'TC70   528316315W036'
		elif kind == '棚车':
			return 'TP64   000000000W036'
		elif kind == '罐车':
			return 'QG17SK 0000000000000'
		else:
			return 'XXXXXXXXXXXXXXXXXXXX'
	
	def get_new_type(self, _root, _type):
		if 'AngleCock' in _root:
			if _type == 'valve':
				_type = 'AnglecockOpen'
			elif _type == 'valveE':
				_type = 'AnglecockClose'
		elif 'KCDoor' in _root:
			if _type == 'door':
				_type = 'Kdoor'
			elif _type == 'window':
				_type = 'Kwindow'
		elif 'Obj' in _root:
			if _type == 'obj':
				_type = 'Object'
		elif 'Steel' in _root:
			if _type == 'obj':
				_type = 'Object'
			elif _type == 'valve':
				_type = 'GtankercapOpen'
			elif _type == 'steel':
				_type = 'Steelcoil'
		elif 'Wheel' in _root:
			if _type == 'pipe':
				_type = 'Wheel'
		return _type

	def thread_insert_to_r_image_label(self, data):
		_get_imageid_sql = 'select dmp.image.id from dmp.image where dmp.image.path=%s'
		_get_labelid_sql = 'select dmp.label.id from dmp.label where dmp.label.type=%s and dmp.label.name=%s'
		_insert_r_image_label_sql = 'insert into dmp.r_image_label (dmp.r_image_label.image_id, dmp.r_image_label.label_id, dmp.r_image_label.data) values (%s, %s, %s)'
		mutex.acquire()
		_image_id = Util.execute_sql(_get_imageid_sql, args=(data.replace('\\', '\\\\'),))
		mutex.release()
		if len(self.import_data[data].keys()) == 0:
			return
		for lbl_type in self.import_data[data].keys():
			_label_type = ''
			if lbl_type == 'D':
				_label_type = '目标检测'
			elif lbl_type == 'C':
				_label_type = '分类'
			elif lbl_type == 'G':
				_label_type = '分割'

			for obj in self.import_data[data][lbl_type]:
				mutex.acquire()
				_label_id = Util.execute_sql(_get_labelid_sql, args=(_label_type, Util.label_object[str(obj[0])]))
				mutex.release()
				if len(_label_id) == 0:
					continue
				try:
					mutex.acquire()
					Util.execute_sql(_insert_r_image_label_sql,
					                 args=(int(_image_id[0][0]), int(_label_id[0][0]), str(obj[1]).strip()),
					                 need_commit=True)
					mutex.release()
				except Exception as e:
					Util.LOG.error(repr(e))
					Util.LOG.debug('sql -> %s' % (_insert_r_image_label_sql,))
					continue

	def thread_insert_to_image(self, data, jpg_or_png=0):
		_insert_image_sql = ''
		if jpg_or_png == 0:
			_insert_image_sql = 'insert into dmp.image(path, code, date, side, line, site, width, height, speed, scale, end, tarpaulin, weather, dmp.image.range, quality, axel_info, calibration_info, state, dmp.image.set) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		elif jpg_or_png == 1:
			_insert_image_sql = 'insert into dmp.r_image_label (dmp.r_image_label.image_id, dmp.r_image_label.label_id, dmp.r_image_label.data) values (%s, %s, %s)'
		mutex.acquire()
		try:
			if jpg_or_png == 0:
				Util.execute_sql(
					_insert_image_sql,
					args=(
						os.path.normpath(data[0]).replace("\\", "\\\\"),
						data[1],
						datetime.datetime.strptime(data[2], '%Y%m%d%H%M%S').strftime("%Y-%m-%d %H:%M:%S"),
						data[3],
						data[4],
						data[5],
						data[6],
						data[7],
						int(data[8]),
						data[9],
						data[10],
						data[11],
						data[12],
						data[13],
						data[14],
						data[15],
						data[16],
						data[17],
						data[18]
					),
					need_commit=True)
			elif jpg_or_png == 1:
				Util.execute_sql(_insert_image_sql, args=(data[0], data[1], data[2]), need_commit=True)
		except Exception as e:
			Util.LOG.error(repr(e))
			Util.LOG.debug('sql -> %s' % (_insert_image_sql % (data[0], data[1], data[2])))
		mutex.release()
		_select_image_sql = 'select dmp.image.id from dmp.image where dmp.image.path=%s'
		mutex.acquire()
		_id = Util.execute_sql(_select_image_sql, args=(os.path.normpath(data[0]).replace('\\', '\\\\')))
		mutex.release()
		if len(_id) > 0:
			return _id[0][0]
		else:
			return

	def gen_import_works(self, ids):
		work = list()
		for _id in ids:
			try:
				_sql = 'select dmp.image.path from dmp.image where dmp.image.id=%s'
				_path = Util.execute_sql(_sql, args=(int(_id),))[0][0]
				_get_r_label = 'select dmp.r_image_label.id from dmp.r_image_label where dmp.r_image_label.image_id=%s'
				_r_id = Util.execute_sql(_get_r_label, args=(int(_id),))
			except Exception as e:
				Util.LOG.error(repr(e))
				Util.LOG.debug('err -> %s' % (_id,))

			work.append((
				_path,
				(_id, _r_id),
				self.import_data[_path] if self.import_data is not None and _path in self.import_data.keys() else dict()
			))
		return work

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
		if self.mode == ID_MODE_EXPORT and self.dvc.GetItemCount() > 0:
			r = Wizard.show_export_wizard(self)
			row = self.dvc.GetItemCount()
			ids = [self.dvc.GetValue(r, 1) for r in range(row) if self.dvc.GetValue(r, 0)]
			if r is not None and len(ids) > 0:
				# for w in self.gen_export_works(ids, r):
				# self.parent.process_work(self.parent.to_export, (self.gen_export_works(ids, r),))
				self.info = {
					'import': {
						'send': [],
						'_send': 0
					},
					'export': {
						'cutting': [],
						'process': [],
						'zoom': [],
						'recv': [],
						'_cutting': 0,
						'_process': 0,
						'_zoom': 0,
						'_recv': 0
					}
				}
				UI_thread(self.mode, (self.gen_export_works(ids, r),), p=self.parent,objs=self.parent.last_query_objects)
			# self.parent.to_export(self.gen_export_works(ids, r))
			# btn = evt.GetEventObject()
			# btn.Disable()
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
		self.info = {
			'import': {
				'send': [],
				'_send': 0
			},
			'export': {
				'cutting': [],
				'process': [],
				'zoom': [],
				'recv': [],
				'_cutting': 0,
				'_process': 0,
				'_zoom': 0,
				'_recv': 0
			}
		}
		self.parent.clear_statisticspanel_data()

	def set_replenish_data(self, data):  # 设置补充操作对象
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