# encoding=utf-8

import wx
import wx.dataview as dv
import wx.aui as aui
import os.path
import logging
import inspect
import os
import datetime
import ImageView
import QueryView
import DataView
import StatisticsView
import CarClassification
import pymysql
from six import BytesIO

ID_Image_view = wx.NewId()
ID_Data_view = wx.NewId()
ID_Query_view = wx.NewId()
ID_Statistics_view = wx.NewId()
ID_About = wx.NewId()
ID_EXIT = wx.NewId()


def _datetime_format(date=None, mode=None):
    if date is None:
        date = datetime.datetime.now()
    if mode == 1:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日'
    elif mode == 2:
        return date.strftime('%Y%m%d%H%M%S')
    elif mode == 3:
        return date.strftime('%m/%d/%Y')
    elif mode == 4:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日 ' + str(date.hour).zfill(2) + ':' + str(date.minute).zfill(2) + ':' + str(date.second).zfill(2)
    elif mode == 5:
        return date.strftime('%Y%m%d')


def _get_logger():
    logger = logging.getLogger('[数据管理平台]')

    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    if not os.path.exists(os.path.join(dirpath, 'log')):
        os.makedirs(os.path.join(dirpath, 'log'))
    handler = logging.FileHandler(os.path.join(dirpath, 'log', _datetime_format(mode=2) + ".log"))

    formatter = logging.Formatter('%(asctime)s %(name)-12s [line:%(lineno)d] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


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
        self.log = _get_logger()
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
        self.db_connect()
        self.last_sql = None

        mb = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "退出")

        view_menu = wx.Menu()
        view_menu.Append(ID_Image_view, "图像视图")
        view_menu.Append(ID_Data_view, "数据视图")
        view_menu.Append(ID_Query_view, "检索视图")
        view_menu.Append(ID_Statistics_view, "统计视图")

        setting_menu = wx.Menu()
        setting_menu.Append(ID_About, "设置")

        mb.Append(file_menu, "文件")
        mb.Append(view_menu, "视图")
        mb.Append(setting_menu, "设置")

        self.SetMenuBar(mb)

        self.statusbar = self.CreateStatusBar(3, wx.STB_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -3, -2])
        self.SetMinSize(wx.Size(400, 300))

        # 初始化弹出菜单
        # self.init_popmenu()

        # 添加面板
        self.add_panel()

        # 加载界面
        # self.load_default_ui()

        # 更新界面
        self._mgr.Update()

        # 事件绑定
        self.bind_event()

    def db_do_sql(self, sql, need_commit=False, is_save=False, update=False):
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if is_save:
            self.last_sql = sql
        if update:
            self.data_view.set_data(data, 1)
            self.statistics_panel.set_data(data)
        if need_commit:
            self.db.commit()
        return data

    def last_query(self):
        self.db_do_sql(self.last_sql, update=True)


    def db_connect(self):
        try:
            self.db = pymysql.connect("localhost", "root", "Passw0rd", "dmp")
            self.cursor = self.db.cursor()
            self.cursor.execute("select * from information_schema.columns where table_schema = 'dmp' and table_name = 'image'")
            data = self.cursor.fetchall()
            self.db_column_info = {k[-3]: {'type': k[7], 'field': k[3]} for k in data}
        except Exception as e:
            self.db = None

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

    def add_panel(self):
        self._mgr.AddPane(self.CreateGrid(), aui.AuiPaneInfo().
                          Name("数据").Caption("数据").MinSize(wx.Size(200,150)).Bottom().Layer(0).Row(0).Position(0).CloseButton(True).MaximizeButton(True))
        self._mgr.AddPane(self.CreateStatisticsCtrl(), aui.AuiPaneInfo().
                          Name("统计").Caption("统计").MinSize(wx.Size(200,150)).Bottom().Layer(0).Row(0).Position(1).CloseButton(True).MaximizeButton(True))
        file_path = 'E:\\code\\jetbrains\\pycharm\\dmp\\TC62BK_202.202.202.2_20171117063710_ZL057_57.jpg'
        self._mgr.AddPane(self.CreateQueryCtrl(), aui.AuiPaneInfo().Name("检索").CenterPane())
        self._mgr.AddPane(self.CreateImageCtrl(file_path), aui.AuiPaneInfo().Name("图像").CenterPane().Hide())
        self._mgr.Update()

    def on_show_query_view(self, event=None):
        self._mgr.GetPane("检索").Show()
        self._mgr.GetPane("图像").Hide()
        self._mgr.Update()

    def on_show_image_view(self, event=None):
        self._mgr.GetPane("图像").Show()
        self._mgr.GetPane("检索").Hide()
        self._mgr.Update()

    def on_show_data_view(self, event=None):
        self._mgr.GetPane("数据").Show().Bottom().Layer(0).Row(0).Position(0)
        self._mgr.Update()

    def on_show_statistics_view(self, event=None):
        self._mgr.GetPane("统计").Show().Bottom().Layer(0).Row(0).Position(0)
        self._mgr.Update()

    def on_folder_add(self, e):
        dd = wx.DirDialog(None)
        dd.ShowModal()
        p = dd.Path
        self.tree.AppendItem(self.tree_folder, p)
        self.tree.ExpandAll()

        m_folder_delete = wx.Menu()
        item = wx.MenuItem(m_folder_delete, wx.NewId(), "删除")
        m_folder_delete.Append(item)
        self.Bind(wx.EVT_MENU, self.on_folder_delete, item)

        self.pop_menu[wx.TreeEvent]["文件夹"][p] = m_folder_delete

    def on_folder_delete(self, e):
        self.current_tree_event.EventObject.Delete(self.current_tree_event.Item)

    def on_server_delete(self, e):
        self.current_tree_event.EventObject.Delete(self.current_tree_event.Item)

    def on_server_setting(self, e):
        sp = SetServer(self)
        self.tree.AppendItem(self.tree_server, sp.Value)
        self.tree.ExpandAll()
        m_server_delete = wx.Menu()
        item = wx.MenuItem(m_server_delete, wx.NewId(), "删除")
        m_server_delete.Append(item)
        self.Bind(wx.EVT_MENU, self.on_server_delete, item)

        self.pop_menu[wx.TreeEvent]["服务器"][sp.Value] = m_server_delete

    def init_popmenu(self):
        m_db = wx.Menu()
        item = wx.MenuItem(m_db, wx.NewId(), "设置")
        m_db.Append(item)
        m_folder_add = wx.Menu()
        item = wx.MenuItem(m_folder_add, wx.NewId(), "添加")
        m_folder_add.Append(item)
        self.Bind(wx.EVT_MENU, self.on_folder_add, item)
        m_server = wx.Menu()
        item = wx.MenuItem(m_server, wx.NewId(), "设置")
        m_server.Append(item)
        self.Bind(wx.EVT_MENU, self.on_server_setting, item)
        m_dataview = wx.Menu()
        item = wx.MenuItem(m_dataview, wx.NewId(), "设置")
        m_dataview.Append(item)
        self.pop_menu = {
            wx.TreeEvent: {
                "数据库": {
                    "root": m_db
                },
                "服务器": {
                    "root": m_server
                },
                "文件夹": {
                    "root": m_folder_add
                }
            },
            wx.dataview.DataViewEvent: m_dataview
        }

    def on_popmenu(self, e):
        if isinstance(e, wx.dataview.DataViewEvent):
            self.PopupMenu(self.pop_menu[type(e)])
        elif isinstance(e, wx.TreeEvent):
            self.current_tree_event = e
            i = e.Item
            name = e.EventObject.GetItemText(i)
            if name not in self.pop_menu[type(e)].keys():
                parent_name = e.EventObject.GetItemText(e.EventObject.GetItemParent(e.Item))
                try:
                    self.PopupMenu(self.pop_menu[type(e)][parent_name][name])
                except:
                    pass
            else:
                self.PopupMenu(self.pop_menu[type(e)][name]["root"])

    def bind_event(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

        self.Bind(wx.EVT_MENU, self.on_show_data_view, id=ID_Data_view)
        self.Bind(wx.EVT_MENU, self.on_show_image_view, id=ID_Image_view)
        self.Bind(wx.EVT_MENU, self.on_show_query_view, id=ID_Query_view)
        self.Bind(wx.EVT_MENU, self.on_show_statistics_view, id=ID_Statistics_view)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_About)

        # self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dataview_row_click)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_popmenu)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.on_popmenu)

    def OnPaneClose(self, event):

        caption = event.GetPane().caption

        if caption in ["图像", "数据"]:
            msg = "确定要关闭吗？"
            dlg = wx.MessageDialog(self, msg, "请注意",
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                event.Veto()
            dlg.Destroy()
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

    def GetDockArt(self):
        return self._mgr.GetArtProvider()

    def DoUpdate(self):
        self._mgr.Update()

    def OnEraseBackground(self, event):
        event.Skip()

    def OnSize(self, event):
        event.Skip()

    def CreateStatisticsCtrl(self):
        self.statistics_panel = StatisticsView.StatisticsView(self)
        return self.statistics_panel

    def CreateImageCtrl(self, file_path):
        self.image_panel = ImageView.ImageView(self, file_path)
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
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        self.tree.AssignImageList(imglist)
        self.tree_db = self.tree.AppendItem(root, "数据库", 0)
        self.tree_server = self.tree.AppendItem(root, "服务器", 0)
        self.tree_folder = self.tree.AppendItem(root, "文件夹", 0)

        self.tree.Expand(root)

        return self.tree


class SetServer(wx.Panel):
    def __init__(self, parent, old_value=None):
        wx.Panel.__init__(self, parent, -1)
        self.Value = None
        dlg = wx.TextEntryDialog(
                self, '请输入数据库IP？',
                '设置', 'Python')

        dlg.SetValue("172.1.10.86")

        if dlg.ShowModal() == wx.ID_OK:
            self.Value = dlg.GetValue()

        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    w, h = wx.DisplaySize()
    frame = MainFrame(None, wx.ID_ANY, "数据管理平台", size=(w, h))
    frame.Show()
    frame.Maximize()
    app.MainLoop()
