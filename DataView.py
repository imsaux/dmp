# encoding=utf-8

import datetime
import os.path
import wx
import wx.dataview as dv

ID_MODE_IMPORT = 0
ID_MODE_EXPORT = 1


class DataView(wx.Panel):
    def __init__(self, parent, data=None, mode=ID_MODE_IMPORT):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.data = data
        self.mode = mode
        self.edit_items = list()
        self.last_edit_row = -1
        self.last_edit_col = -1
        self.dvc = dv.DataViewListCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES # nice alternating bg colors
                                   | dv.DV_VERT_RULES
                                   | dv.DV_MULTIPLE
                                   )

        self.dvc_init()
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)


        b1 = wx.Button(self, label="保存", name="save")
        self.Bind(wx.EVT_BUTTON, self.on_save, b1)
        b2 = wx.Button(self, label="导入", name="import")
        self.Bind(wx.EVT_BUTTON, self.on_import, b2)
        b3 = wx.Button(self, label="导出", name="export")
        self.Bind(wx.EVT_BUTTON, self.on_export, b3)

        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(b1, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(b2, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(b3, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
        self.bind_event()

    def bind_event(self):
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_dbclick)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.on_edit_done)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_STARTED, self.on_edit_start)

    def on_edit_start(self, event):
        self.last_edit_row = event.EventObject.SelectedRow
        self.last_edit_col = event.EventObject.GetColumnPosition(event.EventObject.GetCurrentColumn())

    def on_item_dbclick(self, event):
        img = event.EventObject.GetTextValue(event.EventObject.SelectedRow, 2)
        if os.path.exists(img):
            self.parent.image_panel.set_image(img)
            self.parent.on_show_image_view()

    def on_save(self, evt):
        if len(self.edit_items) > 0:
            for update in self.edit_items:
                _sql = 'update dmp.image set ' + update[0] + ' = ' + str(update[1]) + ' where id=' + str(update[2])
                self.parent.db_do_sql(_sql, need_commit=True)
            self.edit_items = list()

    def on_edit_done(self, event):
        field = self.parent.db_column_info[self.dvc.GetColumn(self.last_edit_col).GetTitle()]['field']
        try:
            if self.parent.db_column_info[event.EventObject.GetCurrentColumn().GetTitle()]['type'] == 'int':
                _new_value = int(event.GetValue())
            elif self.parent.db_column_info[event.EventObject.GetCurrentColumn().GetTitle()]['type'] == 'varchar':
                _new_value = str(event.GetValue())
            image_id = self.dvc.GetValue(self.last_edit_row, 1)
            self.edit_items.append((field, _new_value, image_id))
        except Exception as e:
            self.parent.log.info(repr(e))
        finally:
            self.last_edit_row = -1
            self.last_edit_col = -1


    def on_import(self, evt):
        pass

    def on_export(self, evt):
        pass

    def dvc_init(self):
        i = 0
        self.dvc.AppendToggleColumn('选择', width=80, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        for key in self.parent.db_column_info.keys():
            i += 1
            if i < 14:
                self.dvc.AppendTextColumn(key, width=100)
            else:
                self.dvc.AppendTextColumn(key, width=100, mode=dv.DATAVIEW_CELL_EDITABLE)

        for c in self.dvc.Columns:
            c.Sortable = True
            c.Reorderable = True

    def set_data(self, data, mode):
        if data is not None:
            self.data = data
            self.mode = mode
            self.dvc.DeleteAllItems()
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
                pass