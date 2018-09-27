# encoding=utf-8

import Util
import wx
import wx.dataview as dv
import wx.aui as aui
import ImageView
import QueryView
import DataView
import SettingView
import StatisticsView
from six import BytesIO
import copy
import random


ID_Image_view = wx.NewId()
ID_Data_view = wx.NewId()
ID_Query_view = wx.NewId()
ID_Statistics_view = wx.NewId()
ID_Setting_view = wx.NewId()
ID_About = wx.NewId()
ID_EXIT = wx.NewId()
ID_About_view = wx.NewId()


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



class MainFrame(wx.Frame):
	def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
	             size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
	                                        wx.SUNKEN_BORDER |
	                                        wx.CLIP_CHILDREN):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self._mgr = aui.AuiManager()
		self._mgr.SetManagedWindow(self)

		self.mouse_pos = 0, 0
		self.SetIcon(_get_icon())
		self.tree_db = None
		self.tree_server = None
		self.tree_folder = None
		self.folder_path = None
		self.pop_menu = dict()
		self.current_tree_event = None
		self.current_image = None
		self.db = None
		self.cursor = None
		self.db_column_info = None
		self.last_data = list()
		self.negative_data = list()
		self.last_data_set = set()
		self.last_query_objects = set()
		self.import_param = None
		self.export_param = None
		self.mode = None  # 数据操作模式 0-导入 1-导出
		# self.db_connect()
		self.get_table_info()
		mb = wx.MenuBar()

		file_menu = wx.Menu()
		file_menu.Append(wx.ID_EXIT, "退出")

		view_menu = wx.Menu()
		view_menu.Append(ID_Image_view, "图像视图")
		view_menu.Append(ID_Data_view, "数据视图")
		view_menu.Append(ID_Query_view, "检索视图")
		view_menu.Append(ID_Statistics_view, "统计视图")

		setting_menu = wx.Menu()
		setting_menu.Append(ID_Setting_view, "设置")
		setting_menu.Append(ID_About_view, "关于")

		mb.Append(file_menu, "文件")
		mb.Append(view_menu, "视图")
		mb.Append(setting_menu, "设置")

		self.SetMenuBar(mb)

		self.statusbar = self.CreateStatusBar(3, wx.STB_SIZEGRIP)
		self.statusbar.SetStatusWidths([-2, -3, -2])
		self.SetMinSize(wx.Size(400, 300))

		# 添加面板
		self.add_panel()

		# 更新界面
		self._mgr.Update()

		# 事件绑定
		self.bind_event()

		Util.LOG.info('main已加载')


	def set_mode(self, value):
		self.data_view.mode = value

	def clear_query_objects(self):
		self.last_query_objects = set()

	def set_query_objects(self, query_objects):
		# self.last_query_objects = set(query_objects.split(','))
		self.last_query_objects = set(query_objects)

	def db_do_sql(self, sql, args=None, need_commit=False, update=False, need_last=False, need_clear=False,
	              need_random=-1, for_dataview=False, data_mode=0):
		data = Util.execute_sql(sql, args=args, need_commit=need_commit)
		if len(data) == 0:
			return []
		try:
			all = list()
			all_set = list()
			if int(need_random) > 0:
				_data = list(copy.deepcopy(data))
				while True:
					if len(all) == int(need_random) or len(_data) == 0:
						break
					tmp = random.choice(_data)
					_tmp = list(tmp)
					_tmp.append('负样本')

					if repr(set(tmp)) not in self.last_data_set and _tmp not in all:
						all.append(_tmp)
						all_set.append(set(tmp))
					_data.remove(tmp)
				self.negative_data = all_set
			elif int(need_random) == 0:
				self.negative_data = data
			else:
				for tmp in data:
					if len(self.last_data_set) > 0:
						if tmp not in self.last_data:
							if for_dataview:
								_tmp = list(tmp)
								_tmp.append('原图' if int(need_random) == -1 else '负样本')
								all.append(_tmp)
								all_set.append(set(tmp))
							else:
								all.append(tmp)
								all_set.append(set(tmp))
					else:
						if for_dataview:
							_tmp = list(tmp)
							_tmp.append('原图' if int(need_random) == -1 else '负样本')
							all.append(_tmp)
							all_set.append(set(tmp))
						else:
							all.append(tmp)
							all_set.append(tmp)
			data = all
			if need_last:
				if len(self.last_data) > 0:
					self.last_data.extend(data)
				else:
					self.last_data = data
				self.last_data_set = {repr(x) for x in all_set} | self.last_data_set
		except Exception as e:
			Util.LOG.error(repr(e))
			return []
		if update:
			self.data_view.set_data(data, need_clear)
			if int(need_random) == -1:
				self.statistics_panel.set_data(data, need_clear=need_clear)
			else:
				self.statistics_panel.set_data(data, mode=1, need_clear=need_clear)
		return data

	def clear_dataview_data(self):
		self.data_view.clear_data()

	def clear_statisticspanel_data(self):
		self.statistics_panel.clear_data()

	def resume(self):
		self.data_view.set_data(self.last_data, need_clear=True)
		self.statistics_panel.set_data(self.last_data, need_clear=True)

	def get_table_info(self):
		# _sql = 'select * from information_schema.columns where table_schema = "' + self.db_name + '" and table_name = "image" order by ordinal_postion'
		_sql = 'select column_name, data_type, column_comment from information_schema.columns where table_schema=%s and table_name="image" order by ordinal_position'
		data = Util.execute_sql(_sql, args=(Util.DB_NAME,))
		self.db_column_info = {k[2]: {'type': k[1], 'field': k[0]} for k in data}

	def load_other_ui(self):
		# todo 创建界面布局方案
		all_panes = self._mgr.GetAllPanes()

		for ii in range(len(all_panes)):
			if not all_panes[ii].IsToolbar():
				all_panes[ii].Hide()

		self._mgr.GetPane("tb1").Hide()
		self._mgr.GetPane("tb5").Hide()
		self._mgr.GetPane("test8").Show().Left().Layer(0).Row(0).Position(0)
		self._mgr.GetPane("test10").Show().Bottom().Layer(0).Row(0).Position(0)
		self._mgr.GetPane("html_content").Show()

		perspective_other = self._mgr.SavePerspective()
		self._mgr.LoadPerspective(perspective_other)

	def load_default_ui(self):
		self.on_show_data_view()
		self.on_show_query_view()

	def CreateSetting(self):
		self.setting_view = SettingView.SettingView(self)
		return self.setting_view

	def add_panel(self):
		self._mgr.AddPane(self.CreateGrid(), aui.AuiPaneInfo().
		                  Name("数据").Caption("数据").MinSize(wx.Size(200, 150)).Bottom().Layer(0).Row(0).Position(
			0).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(self.CreateSetting(), aui.AuiPaneInfo().
		                  Name("设置").Caption("设置").MinSize(wx.Size(330, 150)).Right().Layer(0).Row(0).Position(
			0).CloseButton(True).MaximizeButton(True).Hide())
		self._mgr.AddPane(self.CreateStatisticsCtrl(), aui.AuiPaneInfo().
		                  Name("统计").Caption("统计").MinSize(wx.Size(200, 150)).Bottom().Layer(0).Row(0).Position(
			1).CloseButton(True).MaximizeButton(True))
		self._mgr.AddPane(self.CreateQueryCtrl(),
		                  aui.AuiPaneInfo().Name("检索").Caption('检索').MinSize(wx.Size(430, 100)).Left().Layer(0).Row(
			                  0).Position(0).CloseButton(True))
		self._mgr.AddPane(self.CreateImageCtrl(), aui.AuiPaneInfo().Name("图像").CenterPane().Hide())
		self._mgr.Update()

	def on_show_query_view(self, event=None):
		self._mgr.GetPane("检索").Show()
		self._mgr.Update()

	def on_show_image_view(self, event=None):
		self._mgr.GetPane("图像").Show()
		self._mgr.Update()

	def on_show_data_view(self, event=None):
		self._mgr.GetPane("数据").Show().Bottom().Layer(0).Row(0).Position(0)
		self._mgr.Update()

	def on_show_statistics_view(self, event=None):
		self._mgr.GetPane("统计").Show().Bottom().Layer(0).Row(0).Position(0)
		self._mgr.Update()

	def on_show_setting_view(self, event=None):
		self._mgr.GetPane("设置").Show().Right().Layer(0).Row(0).Position(0)
		self._mgr.Update()

	def on_popmenu(self, e):
		if isinstance(e, wx.dataview.DataViewEvent):
			self.PopupMenu(self.pop_menu[type(e)])

	def bind_event(self):
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

		self.Bind(wx.EVT_MENU, self.on_show_data_view, id=ID_Data_view)
		self.Bind(wx.EVT_MENU, self.on_show_image_view, id=ID_Image_view)
		self.Bind(wx.EVT_MENU, self.on_show_query_view, id=ID_Query_view)
		self.Bind(wx.EVT_MENU, self.on_show_statistics_view, id=ID_Statistics_view)
		self.Bind(wx.EVT_MENU, self.on_show_setting_view, id=ID_Setting_view)
		self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_About)

		self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_popmenu)

	def OnPaneClose(self, event):
		# caption = event.GetPane().caption
		#
		# if caption in ["图像", "数据"]:
		#     msg = "确定要关闭吗？"
		#     dlg = wx.MessageDialog(self, msg, "请注意",
		#                            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		#
		#     if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
		#         event.Veto()
		#     dlg.Destroy()
		self._mgr.GetPane("图像").Resizable()
		self._mgr.Update()

	def OnClose(self, event):
		if self.db is not None:
			self.db.close()
		self._mgr.UnInit()
		del self._mgr
		self.Destroy()

	def OnAbout(self, event):
		msg = "wx.aui Demo\n" + \
		      "An advanced window management library for wxWidgets\n" + \
		      "(c) Copyright 2005-2006, Kirix Corporation"
		dlg = wx.MessageDialog(self, msg, "About wx.aui Demo",
		                       wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def OnExit(self, event):
		self.OnClose()

	def DoUpdate(self):
		self._mgr.Update()

	def OnEraseBackground(self, event):
		event.Skip()

	def OnSize(self, event):
		event.Skip()

	def CreateStatisticsCtrl(self):
		self.statistics_panel = StatisticsView.StatisticsView(self)
		return self.statistics_panel

	def CreateImageCtrl(self, file_path=None):
		self.image_panel = ImageView.ImageView(self, file_path=file_path)
		return self.image_panel

	def CreateQueryCtrl(self):
		self.query_panel = QueryView.QueryView(self, self.db_column_info)
		return self.query_panel

	def CreateGrid(self):
		self.data_view = DataView.DataView(self)
		return self.data_view

	def CreateTreeCtrl(self):
		self.tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(160, 250),
		                        wx.TR_DEFAULT_STYLE | wx.NO_BORDER)

		root = self.tree.AddRoot("数据源")

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
		imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
		self.tree.AssignImageList(imglist)
		self.tree_db = self.tree.AppendItem(root, "数据库", 0)
		self.tree_server = self.tree.AppendItem(root, "服务器", 0)
		self.tree_folder = self.tree.AppendItem(root, "文件夹", 0)

		self.tree.Expand(root)

		return self.tree


if __name__ == '__main__':
	_v = '预览版'
	app = wx.App()
	w, h = wx.DisplaySize()
	frame = MainFrame(None, wx.ID_ANY, "数据管理平台 %s" % (_v), size=(w, h))
	frame.Show()
	frame.Maximize()
	app.MainLoop()
