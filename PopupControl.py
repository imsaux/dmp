# encoding=utf-8
import wx
import wx.adv
import wx.lib.masked as masked
from wx.adv import CalendarCtrl
import MyPopupctl


class PopControl(MyPopupctl.MyPopupControl):
    def __init__(self, parent, mode, data, *_args, **_kwargs):
        MyPopupctl.MyPopupControl.__init__(self, *_args, **_kwargs)
        self.win = wx.Window(self, -1, pos=(0, 0), style = 0)
        self.parent = parent
        self.mode = mode
        self.pop_obj = None
        self.selected_items = list()
        if mode == 1:
            self.pop_obj = CalendarCtrl(self.win, -1, pos=(0, 0))
            self.pop_obj.Bind(wx.adv.EVT_CALENDAR, self.on_calendar)
        elif mode == 2:
            if data is not None:
                self.pop_obj = wx.CheckListBox(self.win, -1, (0, 0), wx.DefaultSize, data)
                self.pop_obj.Bind(wx.EVT_CHECKLISTBOX, self.on_checklist_selected)
                self.parent.Bind(wx.EVT_LEFT_UP, self.on_checklist)
        elif mode == 3:
            if data is not None:
                spin = wx.SpinButton(self.win, -1, wx.DefaultPosition, (-1, 20), wx.SP_VERTICAL)
                self.pop_obj = masked.TimeCtrl(
                    self.win,
                    -1,
                    name="time_picker",
                    fmt24hr=True,
                    display_seconds=True,
                    spinButton = spin
                )
                self.pop_obj.SetValue('00:00:00')

        if self.pop_obj is not None:
            bz = self.pop_obj.GetBestSize()
            self.win.SetSize(bz)
            self.SetPopupContent(self.win)

    def on_checklist(self, event):
        self.PopDown()
        event.Skip()


    def on_checklist_selected(self, event):
        self.SetValue(','.join(self.pop_obj.CheckedStrings))
        event.Skip()

    def on_calendar(self, evt):
        self.PopDown()
        date = self.pop_obj.GetDate()
        self.SetValue('%04d%02d%02d' % (date.GetYear(),
                                        date.GetMonth()+1,
                                        date.GetDay()))
        evt.Skip()

    def FormatContent(self):
        if self.mode == 1:
            txtValue = self.GetValue()
            didSet = False
            if len(txtValue) > 0:
                y = int(txtValue[:4])
                m = int(txtValue[4:6]) - 1
                d = int(txtValue[6:8])
                if d > 0 and d < 31:
                    if m >= 0 and m < 12:
                        if y > 1000:
                            self.pop_obj.SetDate(wx.DateTime.FromDMY(d, m, y))
                            didSet = True

            if not didSet:
                self.pop_obj.SetDate(wx.DateTime.Today())
        elif self.mode == 2:
            txtValue = self.GetValue()
            if txtValue == '':
                self.pop_obj.Checked = []
            else:
                try:
                    self.pop_obj.Checked = [self.pop_obj.GetItems().index(x) for x in txtValue.split(',')]
                except Exception as e:
                    self.pop_obj.Checked = []