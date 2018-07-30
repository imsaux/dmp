# encode=utf8

import wx.adv
from wx.adv import Wizard as wiz
from wx.adv import WizardPage
import os.path


def makePageTitle(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer


class Replenish_Select_Mode(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)
        self.value = None
        _list = [
            ''
        ]



class Import_Select_mode(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)
        self.value = None
        _list = [
            '新素材',
            '旧素材'
        ]
        self.rb = wx.RadioBox(
            self, -1, "导入种类", wx.DefaultPosition, wx.DefaultSize,
            _list, 2, wx.RA_SPECIFY_COLS
        )
        self.rb.SetSelection(0)
        self.sizer.Add(self.rb, 0, wx.ALL, 1)

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        if self.rb.GetStringSelection() == '旧素材':
            self.next.GetNext().SetPrev(self)
            return self.next.GetNext()
        else:
            self.next.GetNext().SetPrev(self)
            return self.next

    def GetPrev(self):
        return self.prev


class Import_SetDir(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)
        self.value = None
        self.sizer.Add(wx.StaticText(self, -1, "路径 ", (20, 10)), 0, wx.ALL, 1)
        line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tc = wx.TextCtrl(self, -1, size=(200, -1))
        self.btn = wx.Button(self, -1, size=(20, -1), label='...')
        self.btn.Bind(wx.EVT_BUTTON, self.on_button)
        line_sizer.Add(self.tc, 0, wx.ALL, 5)
        line_sizer.Add(self.btn, 0, wx.ALL, 5)
        self.sizer.Add(line_sizer)
        self.sizer.Add(wx.StaticText(self, -1, "站点 ", (20, 10)), 0, wx.ALL, 1)

        # todo 站点列表


    def on_button(self, event):
        dd_image = wx.DirDialog(self, "请选择文件夹",
                                style=wx.DD_DEFAULT_STYLE
                                      | wx.DD_DIR_MUST_EXIST
                                # | wx.DD_CHANGE_DIR
                                )
        if dd_image.ShowModal() == wx.ID_OK and os.path.exists(dd_image.GetPath()):
            self.tc.SetValue(dd_image.GetPath())

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        if self.prev.rb.GetStringSelection() == '新素材':
            return self.next.GetNext()
        else:
            return self.next

    def GetPrev(self):
        return self.prev


class Import_SetLabel(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)
        self.rb_label = wx.RadioBox(
            self, -1, "标签类型", wx.DefaultPosition, wx.DefaultSize,
            ['分类标签', '目标检测标签', '分割标签'], 2, wx.RA_SPECIFY_COLS
        )
        self.sizer.Add(self.rb_label)
        line_sizer_g = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_label = wx.TextCtrl(self, -1, size=(200, -1))
        btn_g = wx.Button(self, -1, size=(20, -1), label='...')
        btn_g.Bind(wx.EVT_BUTTON, self.on_button_label)
        line_sizer_g.Add(self.tc_label, 0, wx.ALL, 1)
        line_sizer_g.Add(btn_g, 0, wx.ALL, 1)
        self.sizer.Add(wx.StaticText(self, -1, "路径 ", (20, 10)), 0, wx.ALL, 1)
        self.sizer.Add(line_sizer_g, 0, wx.ALL, 1)
        self.sizer.Add(wx.StaticText(self, -1, "尺度 ", (20, 10)), 0, wx.ALL, 1)

        self.tc_scale =wx.TextCtrl(self, -1, size=(200, -1))
        self.sizer.Add(self.tc_scale, 0, wx.ALL, 1)

    def on_button_label(self, event):
        dd_image = wx.DirDialog(self, "请选择文件夹",
                                style=wx.DD_DEFAULT_STYLE
                                      | wx.DD_DIR_MUST_EXIST
                                # | wx.DD_CHANGE_DIR
                                )
        if dd_image.ShowModal() == wx.ID_OK and os.path.exists(dd_image.GetPath()):
            self.tc_label.SetValue(dd_image.GetPath())

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev


class ComfirmPage(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev


class Export_SetScale(wx.adv.WizardPage):
    def __init__(self, parent, title):
        WizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer = makePageTitle(self, title)
        self.SetSize((1000, 600))
        self.sizer.Add(wx.StaticText(self, -1, "尺度 ", (20, 10)), 0, wx.ALL, 1)
        line_sizer_g = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_scale = wx.TextCtrl(self, -1, size=(200, -1))
        line_sizer_g.Add(self.tc_scale, 0, wx.ALL, 1)
        self.sizer.Add(line_sizer_g, 0, wx.ALL, 1)

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev


def show_replenish_wizard(parent):
    pass


def show_import_wizard(parent):
    if parent is not None:
        wizard = wiz(parent, -1, "导入向导")
        page1 = Import_Select_mode(wizard, "设置导入类型")
        wizard.FitToPage(page1)

        page2 = Import_SetDir(wizard, "设置文件夹")
        page3 = Import_SetLabel(wizard, "设置标签")
        page4 = ComfirmPage(wizard, "确认")
        # parent.page1 = page1
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)
        page3.SetNext(page4)
        page4.SetPrev(page3)

        wizard.GetPageAreaSizer().Add(page1)
        if wizard.RunWizard(page1):
            result = dict()
            if page1.rb.GetStringSelection() == '新素材':
                result['image'] = page2.tc.GetValue() if os.path.exists(page2.tc.GetValue()) else ''
            elif page1.rb.GetStringSelection() == '旧素材':
                result['label_type'] = page3.rb_label.GetStringSelection()
                result['label_dir'] = page3.tc_label.GetValue()
                result['image_scale'] = page3.tc_scale.GetValue()
            return result
        else:
            pass


def show_export_wizard(parent):
    if parent is not None:
        wizard = wiz(parent, -1, "导出向导")
        page1 = Export_SetScale(wizard, "设置尺度")
        wizard.FitToPage(page1)
        page2 = ComfirmPage(wizard, "确认")
        page1.SetNext(page2)
        page2.SetPrev(page1)

        wizard.GetPageAreaSizer().Add(page1)
        if wizard.RunWizard(page1):

            _v = page1.tc_scale.GetValue()
            if _v != '':
                v = float(_v)

                if 0 < v < 1:
                    result = dict()
                    result['scale'] = v
                    return result
        else:
            pass

