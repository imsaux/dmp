# encode = utf-8

import wx
import QueryView


class NagetiveAddFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent)
		self.SetSize((800, 600))
		self.SetTitle('添加负样本')
		self.parent = parent
		NAP = QueryView.TestView(self, self.parent.db_column_info, nagetive=True)
		self.Show()
		# self.Maximize()

	def db_do_sql(self, sql, need_commit=False, is_save=False, update=False, need_clear=False):
		return self.parent.db_do_sql(sql, need_commit=need_commit, is_save=is_save, update=update, need_clear=need_clear)

	def set_mode(self, value):
		return self.parent.set_mode(value)

	def clear_query_objects(self):
		return self.parent.clear_query_objects()

	def set_query_objects(self, data):
		return self.parent.set_query_objects(data)

	def on_show_data_view(self):
		return self.parent.on_show_data_view()

	def last_query(self):
		return self.parent.last_query()
