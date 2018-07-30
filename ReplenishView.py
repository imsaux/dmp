# encode=utf8

import wx.lib.agw.labelbook as LB
from wx.lib.agw.fmresources import *


_pageTexts = ['负样本', '补充素材']


class NegativePane(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=0)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.parent = parent
        self.all_sizer = wx.BoxSizer(wx.VERTICAL)
        self.is_enable = False
        self.ui_init()
        self.ui_bind()

    def ui_init(self):
        _tmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_enable = wx.CheckBox(self, -1, "开启")
        _tmp_sizer.Add(self.cb_enable, 0, wx.LEFT, 10)
        bt1 = wx.Button(self, -1, '确认')
        bt1.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.all_sizer.Add(_tmp_sizer, 0, wx.TOP, 0)
        self.all_sizer.Add(bt1, 0, wx.BOTTOM, 0)

    def on_confirm(self, e):
        pass

    def ui_bind(self):
        self.cb_enable.Bind(wx.EVT_CHECKBOX, self.on_cb_enable)

    def on_cb_enable(self, e):
        self.is_enable = e.EventObject.Value


class ReplenishPane(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=0)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.parent = parent
        self.all_sizer = wx.BoxSizer(wx.VERTICAL)
        self.is_enable = False
        self.ui_init()
        self.ui_bind()

    def ui_init(self):
        _tmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_enable = wx.CheckBox(self, -1, "开启")
        _tmp_sizer.Add(self.cb_enable, 0, wx.EXPAND, 0)
        self.all_sizer.Add(_tmp_sizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 0)

    def ui_bind(self):
        self.cb_enable.Bind(wx.EVT_CHECKBOX, self.on_cb_enable)

    def on_cb_enable(self, e):
        self.is_enable = e.EventObject.Value


class ReplenishView(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.initializing = True
        self.book = None
        self._oldTextSize = 1.0
        self.Negative_Pane = None
        self.Replenish_Pane = None
        self.SetProperties()
        self.CreateLabelBook()

        self.CenterOnScreen()

        self.initializing = False
        self.SendSizeEvent()
        self.ui_bind()

    def ui_bind(self):
        self.Bind(wx.EVT_CLOSE, self.on_save)

    def on_save(self, e):
        # todo 保存补充素材参数
        if self.Negative_Pane.is_enable:
            pass
        if self.Replenish_Pane.is_enable:
            pass
        self.Destroy()

    def CreatePages(self):
        self.Negative_Pane = NegativePane(self.book)
        self.Replenish_Pane = ReplenishPane(self.book)
        self.book.AddPage(self.Negative_Pane, '负样本', True, 0)
        self.book.AddPage(self.Replenish_Pane, '补充素材', False, 1)

    def SetProperties(self):
        self.SetTitle("补充素材")
        self.SetSize((1000, 600))

    def CreateLabelBook(self):
        if not self.initializing:
            self.Freeze()
            self.book.Destroy()
        else:
            self.imagelist = self.CreateImageList()

        self.book = LB.LabelBook(self, -1)
        self.book.SetFontSizeMultiple(1.0)
        self.book.SetFontBold(False)

        self.book.SetSelection(0)
        self.book.AssignImageList(self.imagelist)
        self.CreatePages()
        self.book.SetSize(self.book.GetClientSize())

        if not self.initializing:
            self.GetSizer().Layout()
            self.Layout()
            self.Thaw()

        self.SendSizeEvent()

    def CreateImageList(self):
        import os.path
        _pageIcons = ["dialog.png", "expansion.png"]

        imagelist = wx.ImageList(16, 16)
        for img in _pageIcons:
            _base_dir = os.path.dirname(os.path.abspath(__file__))
            newImg = os.path.join(_base_dir, 'image', img)
            bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
            imagelist.Add(bmp)

        return imagelist

    def OnPageChanging(self, event):

        oldsel = event.GetOldSelection()
        newsel = event.GetSelection()
        event.Skip()

    def OnPageChanged(self, event):
        newsel = event.GetSelection()
        event.Skip()

    def OnPageClosing(self, event):
        newsel = event.GetSelection()
        event.Skip()

    def OnPageClosed(self, event):
        newsel = event.GetSelection()
        event.Skip()

    def OnQuit(self, event):
        self.Destroy()

