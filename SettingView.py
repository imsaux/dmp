# encoding=utf-8

import datetime
import os.path
import wx
import wx.lib.scrolledpanel as scrolled

class SettingView(scrolled.ScrolledPanel):
    def __init__( self, parent, log ):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        # wx.Panel.__init__( self, parent, -1 )
        self.log = log
        # panel = wx.Panel( self, -1 )
        vs = wx.BoxSizer( wx.VERTICAL )

        box1_title = wx.StaticBox( self, -1, "数据库" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=2 )

        self.group1_ctrls = []
        st1 = wx.StaticText( self, -1, "数据库IP")
        st2 = wx.StaticText( self, -1, "端口")
        st3 = wx.StaticText( self, -1, "用户名")
        st4 = wx.StaticText( self, -1, "密码")
        text1 = wx.TextCtrl( self, -1, "" )
        text2 = wx.TextCtrl( self, -1, "" )
        text3 = wx.TextCtrl( self, -1, "" )
        text4 = wx.TextCtrl( self, -1, "" )
        self.group1_ctrls.append((st1, text1))
        self.group1_ctrls.append((st2, text2))
        self.group1_ctrls.append((st3, text3))
        self.group1_ctrls.append((st4, text4))

        for st, text in self.group1_ctrls:
            grid1.Add( st, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid1.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        box1.Add(grid1, 0, wx.LEFT|wx.ALL, 5)
        vs.Add(box1, 0, wx.LEFT|wx.ALL, 5)

        box2_title = wx.StaticBox( self, -1, "服务器" )
        box2 = wx.StaticBoxSizer( box2_title, wx.VERTICAL )
        grid2 = wx.FlexGridSizer( cols=2 )

        self.group2_ctrls = []
        st1 = wx.StaticText( self, -1, "服务器IP")
        st2 = wx.StaticText( self, -1, "端口")
        text1 = wx.TextCtrl( self, -1, "" )
        text2 = wx.TextCtrl( self, -1, "" )
        self.group2_ctrls.append((st1, text1))
        self.group2_ctrls.append((st2, text2))

        for st, text in self.group2_ctrls:
            grid2.Add( st, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid2.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        box2.Add(grid2, 0, wx.LEFT|wx.ALL, 5)
        vs.Add(box2, 0, wx.LEFT|wx.ALL, 5)


        box3_title = wx.StaticBox(self, -1, "临时目录")
        box3 = wx.StaticBoxSizer(box3_title, wx.VERTICAL)
        grid3 = wx.FlexGridSizer(cols=3)
        self.group3_ctrls = []
        st1 = wx.StaticText( self, -1, "原图")
        st2 = wx.StaticText( self, -1, "补充素材")
        st3 = wx.StaticText( self, -1, "裁剪素材")
        st4 = wx.StaticText( self, -1, "负样本")
        text1 = wx.TextCtrl( self, -1, "" )
        text2 = wx.TextCtrl( self, -1, "" )
        text3 = wx.TextCtrl( self, -1, "" )
        text4 = wx.TextCtrl( self, -1, "" )
        bt1 = wx.Button(self, -1, '选择')
        bt2 = wx.Button(self, -1, '选择')
        bt3 = wx.Button(self, -1, '选择')
        bt4 = wx.Button(self, -1, '选择')
        self.group3_ctrls.append((st1, text1, bt1))
        self.group3_ctrls.append((st2, text2, bt2))
        self.group3_ctrls.append((st3, text3, bt3))
        self.group3_ctrls.append((st4, text4, bt4))

        for st, text, bt in self.group3_ctrls:
            grid3.Add( st, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid3.Add( text, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            grid3.Add( bt, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        box3.Add(grid3, 0, wx.LEFT|wx.ALL, 5)
        vs.Add(box3, 0, wx.LEFT|wx.ALL, 5)

        self.SetSizer(vs)
        self.SetupScrolling()
        # vs.Fit(panel)
        # panel.Move((50,50))
        # self.panel = panel
