# encoding=utf-8
import wx
import wx.adv
import PopupControl
import wx.lib.masked as masked
import copy


class QueryView(wx.Panel):
    def __init__(self, parent, query_items=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        if query_items is None:
            return
        self.query_items = query_items
        self.parent = parent
        self.gbs = gbs = wx.GridBagSizer(vgap=len(query_items.keys())+1, hgap=8)
        self.row = 1
        self.col = 0
        checklist = []
        self.controls = dict()
        label_type = [
            '分类',
            '目标检测',
            '分割'
        ]
        label_objects = [
            '篷布飘起',
            '篷布',
            '篷布破损',
            '火灾',
            '货物撒漏',
            '烟雾',
            '棚车车门开启',
            '棚车车窗开启',
            '客车车门',
            '客车车窗',
            '敞车下门门栓开启',
            '车轮',
            '异物',
            '非异物',
            '闲杂人员扒乘',
            '客车电池箱盖开启',
            '风管',
            '闸链',
            '折角塞门开启',
            '折角塞门关闭',
            '罐车盖开启',
            '卷钢',
            '尾车特征区',
            '车厢连接处',
            '敞车中门'
        ]
        alarm_type = [
            '侧面车门',
            '侧面车窗',
            '侧面异物',
            '侧面动车注水口',
            '走行部尾部软管未吊起',
            '走行部闸链拉紧',
            '走行部折角塞门异常',
            '走行部软管连接异常',
            '走行部敞车下门门栓异常',
            '走行部尾车',
            '顶部异物',
            '顶部卷钢',
            '顶部盖开启',
            '顶部篷布破损'
        ]
        for item in query_items.keys():

            if query_items[item]['field'] in ['id', 'path']:
                pass # 不出现在查询视图中
            else:
                if query_items[item]['field'] == 'datetime':
                    line_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
                    gbs.Add(wx.StaticText(self, -1, '采集日期'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()
                    self.ctr_date_from = PopupControl.PopControl(self, 1, checklist, self, -1, pos=(30, 30))
                    line_sizer1.Add(self.ctr_date_from)
                    line_sizer1.Add(wx.StaticText(self, -1, "  至  "))
                    self.ctr_date_to = PopupControl.PopControl(self, 1, checklist, self, -1, pos=(30, 30))
                    line_sizer1.Add(self.ctr_date_to)
                    gbs.Add(line_sizer1, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()

                    line_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
                    gbs.Add(wx.StaticText(self, -1, '采集时间'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()
                    self.ctr_time_from = masked.Ctrl( self, -1, "",
                                    autoformat='24HRTIMEHHMMSS',
                                    demo=True,
                                    name='24HRTIME')
                    self.ctr_time_from.SetValue('00:00:00')
                    line_sizer2.Add(self.ctr_time_from)
                    line_sizer2.Add(wx.StaticText(self, -1, "  至  "))
                    self.ctr_time_to = masked.Ctrl( self, -1, "",
                                    autoformat='24HRTIMEHHMMSS',
                                    demo=True,
                                    name='24HRTIME')
                    self.ctr_time_to.SetValue('23:59:59')
                    line_sizer2.Add(self.ctr_time_to)
                    gbs.Add(line_sizer2, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()
                elif query_items[item]['field'] in ['speed', 'scale', 'width', 'height']: # 范围
                    line_sizer = wx.BoxSizer(wx.HORIZONTAL)

                    gbs.Add(wx.StaticText(self, -1, item), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()
                    ctrl1 = wx.TextCtrl(self, -1, "", size=(120, -1))
                    setattr(self, 'ctr' + '_' + query_items[item]['field'] + '_from', ctrl1)
                    line_sizer.Add(ctrl1)
                    line_sizer.Add(wx.StaticText(self, -1, "  至  "))
                    ctrl2 = wx.TextCtrl(self, -1, "", size=(120, -1))
                    setattr(self, 'ctr' + '_' + query_items[item]['field'] + '_to', ctrl2)
                    line_sizer.Add(ctrl2)

                    gbs.Add(line_sizer, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()
                elif query_items[item]['field'] in ['status', 'quality_level', 'line', 'side', 'site', 'weather', 'set_type']:
                    line_sizer = wx.BoxSizer(wx.HORIZONTAL)

                    gbs.Add(wx.StaticText(self, -1, item), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()

                    _sql = 'SELECT %s FROM image group by %s' %(query_items[item]['field'], query_items[item]['field'])
                    _data = self.parent.db_do_sql(_sql)
                    _list = [str(x[0]) for x in _data]
                    ctrl = PopupControl.PopControl(self, 2, _list, self, -1, pos=(30, 30))
                    setattr(self, 'ctr'+'_'+query_items[item]['field']+'_select', ctrl)
                    line_sizer.Add(ctrl)
                    gbs.Add(line_sizer, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()
                elif query_items[item]['field'] in ['code']:
                    dct = dict()

                    _sql = 'SELECT %s FROM dmp.image group by %s' %(query_items[item]['field'], query_items[item]['field'])
                    _data = self.parent.db_do_sql(_sql)
                    _list = [str(x[0]) for x in _data]
                    for c in _list:
                        if 'X' * 20 == c:
                            continue
                        if c[0] == 'J' and c[:3] != 'JSQ':
                            if 'J' not in dct.keys():
                                dct['J'] = list()
                            dct['J'].append(str(c[1:4]))
                        elif c[0] == 'K' or ' D ' in c:
                            if c[1:4] not in dct.keys():
                                dct[c[1:4]] = list()
                            dct[c[1:4]].append(str(c[4:6]))
                        else:
                            if c[1] not in dct.keys():
                                dct[c[1]] = list()
                            dct[c[1]].append(str(c[2:7]))
                    line_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
                    gbs.Add(wx.StaticText(self, -1, '车种'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()
                    ctrl = PopupControl.PopControl(self, 2, list(dct.keys()), self, -1, pos=(30, 30))
                    setattr(self, 'ctr' + '_' + query_items[item]['field'] + '_type', ctrl)
                    line_sizer1.Add(ctrl)
                    gbs.Add(line_sizer1, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()

                    line_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
                    gbs.Add(wx.StaticText(self, -1, '车型'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
                    self.update_pos()
                    ctrl = PopupControl.PopControl(self, 2, [x[0] for x in list(dct.values())], self, -1, pos=(30, 30))
                    setattr(self, 'ctr' + '_' + query_items[item]['field'] + '_kind', ctrl)
                    line_sizer2.Add(ctrl)
                    gbs.Add(line_sizer2, (self.row, self.col), flag=wx.ALIGN_LEFT)
                    self.update_pos()

                else:
                    checklist.append(item)
        if len(checklist) > 0:
            line_sizer = wx.BoxSizer(wx.HORIZONTAL)
            gbs.Add(wx.StaticText(self, -1, '其他'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
            self.update_pos()
            ctrl = PopupControl.PopControl(self, 2, checklist, self, -1, pos=(30, 30))
            setattr(self, 'ctr_other', ctrl)
            line_sizer.Add(ctrl)
            gbs.Add(line_sizer, (self.row, self.col), flag=wx.ALIGN_LEFT)
            self.update_pos()

        line_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        gbs.Add(wx.StaticText(self, -1, '标签类型'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
        self.update_pos()
        ctrl = PopupControl.PopControl(self, 2, label_type, self, -1, pos=(30, 30))
        setattr(self, 'ctr_label_type', ctrl)
        line_sizer1.Add(ctrl)
        gbs.Add(line_sizer1, (self.row, self.col), flag=wx.ALIGN_LEFT)
        self.update_pos()

        line_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        gbs.Add(wx.StaticText(self, -1, '检测项'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
        self.update_pos()
        ctrl = PopupControl.PopControl(self, 2, label_objects, self, -1, pos=(30, 30))
        setattr(self, 'ctr_label_object', ctrl)

        line_sizer2.Add(ctrl)
        gbs.Add(line_sizer2, (self.row, self.col), flag=wx.ALIGN_LEFT)
        self.update_pos()


        line_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        gbs.Add(wx.StaticText(self, -1, '报警类型'), (self.row, self.col), flag=wx.ALIGN_RIGHT)
        self.update_pos()
        ctrl = PopupControl.PopControl(self, 2, alarm_type, self, -1, pos=(30, 30))
        setattr(self, 'ctr_alarm_type', ctrl)

        line_sizer3.Add(ctrl)
        gbs.Add(line_sizer3, (self.row, self.col), flag=wx.ALIGN_LEFT)
        self.update_pos()




        self.btn_query = wx.Button(self, -1, '检索')
        self.btn_query.Bind(wx.EVT_BUTTON, self.on_query_click)
        gbs.Add(self.btn_query, (self.row+1, 0), (1, 8), flag=wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(gbs, wx.ALIGN_CENTER)
        self.SetSizer(box)

    def update_pos(self):
        if self.col != 0:
            if self.col + 1 < 8:
                self.col += 1
            else:
                self.col = 0
                self.row += 1
        else:
            self.col += 1

    def on_query_click(self, event):
        base_sql = 'SELECT * FROM dmp.image where 1=1'
        for item in dir(self):
            if 'ctr_' in item:
                data = getattr(self, item).GetValue()
                if data == '':
                    continue
                if 'date_from' in item:
                    base_sql += ' AND LEFT(date_format(datetime, "%Y%m%d“), 8) >= ' + data
                elif 'date_to' in item:
                    base_sql += ' AND LEFT(date_format(datetime, "%Y%m%d“), 8) <= ' + data
                elif 'time_from' in item:
                    base_sql += ' AND LEFT(date_format(datetime, "%k%i%s"), 8) >= ' + ''.join(data.split(':'))
                elif 'time_to' in item:
                    base_sql += ' AND LEFT(date_format(datetime, "%k%i%s"), 8) <= ' + ''.join(data.split(':'))
                elif 'ctr_other' == item:
                    fields = [self.query_items[x]['field'] for x in data.split(',')]
                    for field in fields:
                        base_sql += ' AND ' + field + '=1'
                elif 'ctr_code_type' == item:
                    base_sql += ' AND (0'
                    for type in data.split(','):
                        if type == 'J':
                            base_sql += ' OR substring(code, 1, 1) = "J"'
                        elif type == 'K':
                            base_sql += ' OR substring(code, 1, 1) = "K"'
                        elif type == 'D':
                            base_sql += ' OR substring(code, 1, 1) = "D"'
                        else:
                            base_sql += ' OR substring(code, 2, 1) = "' + type + '"'
                    base_sql += ')'
                elif 'ctr_code_kind' == item:
                    base_sql += ' AND (0'
                    for kind in data.split(','):
                        base_sql += ' OR code like "%' + kind + '%"'
                    base_sql += ')'
                elif 'ctr_label_type' == item:
                    _in_ = ''
                    for i in data.split(','):
                        if _in_ == '':
                            _in_ += '"' + i + '"'
                        else:
                            _in_ += ',"' + i + '"'
                    base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.type in (' + _in_ + ')))'
                elif 'ctr_label_object' == item:
                    _in_ = ''
                    for i in data.split(','):
                        if _in_ == '':
                            _in_ += '"' + i + '"'
                        else:
                            _in_ += ',"' + i + '"'
                    base_sql += ' AND id in (SELECT ril.image_id FROM dmp.r_image_label as ril WHERE ril.label_id in (SELECT l.id FROM dmp.label as l WHERE l.name in (' + _in_ + ')))'
                elif 'ctr_alarm_type' == item:
                    _in_ = ''
                    for i in data.split(','):
                        if _in_ == '':
                            _in_ += '"' + i + '"'
                        else:
                            _in_ += ',"' + i + '"'
                    base_sql += ' AND id in (SELECT ria.image_id FROM dmp.r_image_alarm as ria WHERE ria.alarm_id in (SELECT a.id FROM dmp.alarm as a WHERE a.name in (' + _in_ + ')))'

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
        self.parent.db_do_sql(base_sql, is_save=True, update=True)