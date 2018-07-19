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
        self.dvc = dv.DataViewListCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES # nice alternating bg colors
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
        b2 = wx.Button(self, label="还原", name="first")
        self.Bind(wx.EVT_BUTTON, self.on_first, b2)
        # b3 = wx.Button(self, label="导出", name="export")
        # self.Bind(wx.EVT_BUTTON, self.on_export, b3)

        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        # btnbox.Add(b1, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(b2, 0, wx.LEFT|wx.RIGHT, 5)
        # btnbox.Add(b3, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_refill_data)

    def fill_data(self, refresh=False):
        self.dvc.DeleteAllItems()
        self._all_data = list()
        for id in [x[0] for x in self.data]:
            _sql = "SELECT (select concat(l.name,'-', l.type) from dmp.label l where id=ril.label_id), count(label_id), image_id FROM dmp.r_image_label ril where image_id=" + str(id) +"  group by label_id, image_id;"
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

    def sum_result(self, data, mode=0):
        _sum_ = dict()
        self.dvc.AppendItem(['素材数量', len(data)])
        if mode == 0:
            for item in data:
                if len(item) > 0:
                    for i in item:
                        if i[0] not in _sum_.keys():
                            _sum_[i[0]] = 0
                        _sum_[i[0]] += i[1]
        elif mode == 1:
            for item in data:
                if item[0] not in _sum_.keys():
                    _sum_[item[0]] = 0
                _sum_[item[0]] += item[1]
        for key in _sum_.keys():
            self.dvc.AppendItem([key, _sum_[key]])

    def on_refill_data(self, event):
        item = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 0)
        if item != '素材数量':
            if self.re_fill_enable:
                self.re_fill_data(item)
        event.Skip()

    def re_fill_data(self, item):
        self.dvc.DeleteAllItems()
        items = []
        ids = []
        for x in [x for x in self._all_data if len(x) > 0]:
            for y in x:
                if y[0] == item:
                    items.append(x)
                    ids.append(y[2])
        self.sum_result(items)
        _in_ = ''
        for i in ids:
            if _in_ == '':
                _in_ += '"' + str(i) + '"'
            else:
                _in_ += ',"' + str(i) + '"'

        _sql = 'select * from dmp.image where id in(' + _in_ + ')'
        self.parent.db_do_sql(_sql, update=True)
        self.re_fill_enable = False

    def set_data(self, data):
        if data is not None:
            self.data = data
            self.fill_data()

    def on_first(self, event):
        self.parent.last_query()