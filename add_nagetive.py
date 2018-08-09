# encode = utf-8

import wx
import QueryView


class NagetiveAddFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent)
		self.SetSize((800, 600))
		self.SetTitle('添加负样本')
		self.parent = parent
		NAP = QueryView.QueryView(self, None, query_items=self.parent.db_column_info, nagetive=True)
		self.Show()
		# self.Maximize()

	def db_do_sql(self, sql, need_commit=False, update=False, need_last=False, need_clear=False, need_random=-1, for_dataview=False):
		return self.parent.db_do_sql(sql, need_commit=need_commit, update=update, need_last=need_last, need_random=need_random, for_dataview=for_dataview, data_mode=1)

	def set_mode(self, value):
		return self.parent.set_mode(value)

	def clear_query_objects(self):
		return self.parent.clear_query_objects()

	def clear_dataview_data(self):
		return self.parent.clear_dataview_data()

	def set_query_objects(self, data):
		return self.parent.set_query_objects(data)

	def on_show_data_view(self):
		return self.parent.on_show_data_view()

	def last_query(self):
		return self.parent.last_query()
