# encoding=utf-8
import wx
import copy
import os
import PopupControl
import ImageUtil
import Util


class ImageView(wx.Panel):
    def __init__(self, parent, file_path=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.background = wx.Brush(self.GetBackgroundColour())
        self.start_pos = None
        self.end_pos = None
        self.overlay = wx.Overlay()
        self.parent = parent
        self.objects = {
            ImageUtil.ID_CAR_CALIBRATION: [],
            ImageUtil.ID_AXLE_X_CALIBRATION: [],
            ImageUtil.ID_AXLE_Y_CALIBRATION: [],
            ImageUtil.ID_RAIL_Y_CALIBRATION: [],
            ImageUtil.ID_OUTLINE_CALIBRATION: [],
            ImageUtil.ID_NEW_AXLE_CALIBRATION: [],
            ImageUtil.ID_B_LABEL: [],
            ImageUtil.ID_P_LABEL: [],
            ImageUtil.ID_G_LABEL: [],
            ImageUtil.ID_NONE: []
        }
        self.zoom_ratio = 0
        self.unit_ratio = 0.25
        self.show_pos = 0, 0
        if file_path is not None:
            self.to_show = wx.Bitmap(file_path)
        else:
            self.to_show = None
        self.draw_mode = ImageUtil.ID_NONE
        view_object = [
            "车厢",
            "车轴中心",
            "铁轨",
            "轮廓",
            "车轴",
            "分类标签",
            "目标检测标签",
            "分割标签"
        ]
        self.move_end_pos = self.move_start_pos = 0, 0
        self.diff = 0, 0
        self.macro_diff = 0, 0
        self.dragable = False
        self.last_background_image_pos = None
        self.filter = PopupControl.PopControl(self, 2, view_object, self, -1, pos=(30, 30))
        # self.funcs = wx.ComboBox(self, -1, choices=list,
        #                          size=(150, -1),
        #                          style=wx.CB_READONLY)
        # self.funcs.SetSelection(0)
        # self.funcs.SetToolTip('选择功能')
        # self.overlayPenWidth = wx.SpinCtrl(self, -1, value='',
        #                                    size=(75, -1),
        #                                    style=wx.SP_ARROW_KEYS,
        #                                    min=1, max=24, initial=1)
        # self.overlayPenWidth.SetToolTip('线宽')

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.filter, 0, wx.ALL, 5)
        # sizer.Add(self.overlayPenWidth, 0, wx.ALL, 5)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(sizer, 0)
        box.Add((1, 1), 1)

        self.SetSizer(box)
        self.bind_event()
        self.on_size()

    def refresh_image(self, file_path):
        self.to_show = wx.Bitmap(file_path)
        self.Refresh()

    def bind_event(self):
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_draw_mode)

    def get_now_ratio(self):
        return self.zoom_ratio * self.unit_ratio

    def on_mouse_wheel(self, e):
        # 向上120
        # 向下-120
        v = e.GetWheelRotation()
        self.end_pos = e.GetPosition()
        if v > 0:  # 放大
            self.zoom_ratio += 1
        elif v < 0:  # 缩小
            if self.zoom_ratio > 0:
                self.zoom_ratio -= 1
        else:
            pass
        self.Refresh()

    def set_draw_mode(self, event=None, mode=ImageUtil.ID_NONE):
        if event is not None:
            name = event.EventObject.StringSelection
            if name == "车厢标定":
                self.draw_mode = ImageUtil.ID_CAR_CALIBRATION
            elif name == "车轴标定":
                self.draw_mode = ImageUtil.ID_AXLE_Y_CALIBRATION
            elif name == "铁轨标定":
                self.draw_mode = ImageUtil.ID_RAIL_Y_CALIBRATION
            elif name == "轮廓标定":
                self.draw_mode = ImageUtil.ID_OUTLINE_CALIBRATION
            elif name == "调整车轴":
                self.draw_mode = ImageUtil.ID_AXLE_X_CALIBRATION
            elif name == "添加车轴":
                self.draw_mode = ImageUtil.ID_NEW_AXLE_CALIBRATION
            elif name == "分类标签":
                self.draw_mode = ImageUtil.ID_G_LABEL
            elif name == "目标检测标签":
                self.draw_mode = ImageUtil.ID_B_LABEL
            elif name == "分割标签":
                self.draw_mode = ImageUtil.ID_P_LABEL
            else:
                self.draw_mode = ImageUtil.ID_NONE
        else:
            self.draw_mode = mode

    def set_image(self, filepath):
        if os.path.exists(filepath):
            self.to_show = wx.Bitmap(filepath)
        self.Refresh()

    def on_left_down(self, event):
        self.CaptureMouse()
        self.start_pos = event.GetPosition()
        self.SetFocus()

    def on_right_down(self, event):
        self.CaptureMouse()
        self.move_start_pos = event.GetPosition()
        self.SetFocus()

    def on_right_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.dragable = False
        self.move_end_pos = self.move_start_pos = 0, 0
        self.show_pos = self.show_pos[0] + self.diff[0], self.show_pos[1] + self.diff[1]
        self.diff = 0, 0
        self.macro_diff = 0, 0

    def draw_background_image(self, dc):
        if self.to_show is not None:
            img = self.to_show.ConvertToImage()
            now_ratio = self.get_now_ratio()
            if now_ratio != 0:
                img = img.Scale(self.GetClientSize()[0] * (1 + now_ratio), self.GetClientSize()[1] * (1 + now_ratio))
            else:
                img = img.Scale(self.GetClientSize()[0], self.GetClientSize()[1])
            bmp = wx.Bitmap(img)
            dc.DrawBitmap(bmp, self.show_pos[0] + self.diff[0], self.show_pos[1] + self.diff[1])

    def draw_car_calibration(self, dc):
        # 车厢
        try:
            self.draw_rect(dc, id=ImageUtil.ID_CAR_CALIBRATION, color=wx.RED, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_axel_y_calibration(self, dc):
        # 车轴
        try:
            x, y = self.GetClientSize()
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            self.draw_line(dc, p1, p2, id=ImageUtil.ID_AXLE_Y_CALIBRATION, color=wx.YELLOW, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))
    
    def draw_axel_x_calibration(self, dc):
        # 调整车轴
        try:
            x, y = self.GetClientSize()
            # x
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            # 查询图片中车轴信息，并依次显示
            self.draw_line(dc, p1, p2, color=wx.YELLOW, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_rail_y_calibration(self, dc, id):
        # 铁轨
        try:
            x, y = self.GetClientSize()
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            self.draw_line(dc, p1, p2, id=id, color=wx.BLUE, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_rect(self, dc, rect=None, id=ImageUtil.ID_NONE, color=wx.RED, style=wx.PENSTYLE_SOLID, alpha=125):  # 画矩形透明区域
        # dc -> 绘图上下文，必需
        # rect -> wx.Rect类型，由外部传入
        # id -> int类型，标识图形类别
        # color -> 颜色
        # style -> 样式
        if self.start_pos is None or self.end_pos is None:
            return
        try:
            if rect is None:
                rect = wx.Rect(topLeft=self.start_pos, bottomRight=self.end_pos)
                self.objects[id].append(rect)
                odc = wx.DCOverlay(self.overlay, dc)
                odc.Clear()
                self.overlay.Reset()

                dc = wx.GCDC(dc)
                dc.SetPen(wx.Pen(colour=color,
                                #  width=self.overlayPenWidth.GetValue(),
                                 style=style))

                bc = wx.RED
                bc = wx.Colour(bc.red, bc.green, bc.blue, alpha=alpha)
                dc.SetBrush(wx.Brush(bc))
            else:
                dc = wx.GCDC(dc)
                dc.SetPen(wx.Pen(colour=color,
                                #  width=self.overlayPenWidth.GetValue(),
                                 style=style))

                bc = wx.RED
                bc = wx.Colour(bc.red, bc.green, bc.blue, alpha=alpha)
                dc.SetBrush(wx.Brush(bc))
            dc.DrawRectangle(rect)


        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_line(self, dc, p1, p2, id=ImageUtil.ID_NONE, color=wx.RED, style=wx.PENSTYLE_SOLID):
        dc.SetPen(wx.Pen(colour=color, style=style))
        x1, y1 = p1
        x2, y2 = p2
        dc.DrawLine(
            x1,
            y1,
            x2,
            y2
        )
        self.objects[id].append(
            [
                id,
                p1,
                p2
            ]
        )

    def on_mouse_move(self, event):
        # 绘图
        if event.Dragging() and event.LeftIsDown():
            if self.draw_mode == ImageUtil.ID_CAR_CALIBRATION:
                self.end_pos = event.GetPosition()
                self.Refresh()

        # 拖动
        if event.Dragging() and event.RightIsDown():
            if self.move_end_pos == (0, 0):
                tmp = copy.deepcopy(self.move_start_pos)
            else:
                tmp = copy.deepcopy(self.move_end_pos)
            self.move_end_pos = event.GetPosition()
            self.diff = self.move_end_pos[0] - self.move_start_pos[0], self.move_end_pos[1] - self.move_start_pos[1]
            self.macro_diff = self.move_end_pos[0] - tmp[0], self.move_end_pos[1] - tmp[1]
            self.dragable = True
            self.Refresh()

    def on_erase(self, event):
        pass

    def on_left_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        # odc = wx.DCOverlay(self.overlay, self.dc)
        # odc.Clear()

        self.start_pos = self.end_pos
        self.end_pos = event.Position
        # self.Refresh()
        event.Skip()

    def on_size(self, event=None):
        if event:
            event.Skip()
        self.Refresh()

    def draw_objects(self, dc):
        if len(self.objects[ImageUtil.ID_CAR_CALIBRATION]) > 0:
            rect = self.objects[ImageUtil.ID_CAR_CALIBRATION][-1]
            x = rect.GetX()
            y = rect.GetY()
            rect.SetX(x + self.macro_diff[0])
            rect.SetY(y + self.macro_diff[1])
            self.draw_rect(dc, rect=rect)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        self.draw_background_image(dc)
        self.draw_objects(dc)
        if self.dragable is False:
            if self.draw_mode == ImageUtil.ID_CAR_CALIBRATION:
                self.draw_rect(dc, id=ImageUtil.ID_CAR_CALIBRATION)


class test(wx.Panel):
    def __init__(self, parent, file_path):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.CLIP_CHILDREN)
        self.background = wx.Brush(self.GetBackgroundColour())
        self.start_pos = None
        self.end_pos = None
        self.overlay = wx.Overlay()
        self.parent = parent
        self.objects = {
            ImageUtil.ID_CAR_CALIBRATION: [],
            ImageUtil.ID_AXLE_X_CALIBRATION: [],
            ImageUtil.ID_AXLE_Y_CALIBRATION: [],
            ImageUtil.ID_RAIL_Y_CALIBRATION: [],
            ImageUtil.ID_OUTLINE_CALIBRATION: [],
            ImageUtil.ID_NEW_AXLE_CALIBRATION: [],
            ImageUtil.ID_B_LABEL: [],
            ImageUtil.ID_P_LABEL: [],
            ImageUtil.ID_G_LABEL: [],
            ImageUtil.ID_NONE: []
        }
        self.zoom_ratio = 0
        self.unit_ratio = 0.25
        self.show_pos = 0, 0
        self.to_show = wx.Bitmap(file_path)
        self.draw_mode = ImageUtil.ID_NONE
        list = [
            "请选择",
            "车厢标定",
            "车轴标定",
            "铁轨标定",
            "轮廓标定",
            "调整车轴",
            "添加车轴",
            "分类标签",
            "目标检测标签",
            "分割标签"
        ]
        self.move_start_pos = None
        self.move_end_pos = None
        self.diff = 0, 0
        self.last_background_image_pos = None
        self.funcs = wx.ComboBox(self, -1, choices=list,
                                 size=(150, -1),
                                 style=wx.CB_READONLY)
        self.funcs.SetSelection(0)
        self.funcs.SetToolTip('选择功能')
        self.overlayPenWidth = wx.SpinCtrl(self, -1, value='',
                                           size=(75, -1),
                                           style=wx.SP_ARROW_KEYS,
                                           min=1, max=24, initial=1)
        self.overlayPenWidth.SetToolTip('线宽')

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.funcs, 0, wx.ALL, 5)
        sizer.Add(self.overlayPenWidth, 0, wx.ALL, 5)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(sizer, 0)
        box.Add((1, 1), 1)

        self.SetSizer(box)
        self.bind_event()
        self.on_size()

    def bind_event(self):
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.set_draw_mode)

    def get_now_ratio(self):
        return self.zoom_ratio * self.unit_ratio

    def on_mouse_wheel(self, e):
        # 向上120
        # 向下-120
        v = e.GetWheelRotation()
        self.end_pos = e.GetPosition()
        if v > 0:  # 放大
            self.zoom_ratio += 1
        elif v < 0:  # 缩小
            if self.zoom_ratio > 0:
                self.zoom_ratio -= 1
        else:
            pass
        self.Refresh()

    def set_draw_mode(self, event=None, mode=ImageUtil.ID_NONE):
        if event is not None:
            name = event.EventObject.StringSelection
            if name == "车厢标定":
                self.draw_mode = ImageUtil.ID_CAR_CALIBRATION
            elif name == "车轴标定":
                self.draw_mode = ImageUtil.ID_AXLE_Y_CALIBRATION
            elif name == "铁轨标定":
                self.draw_mode = ImageUtil.ID_RAIL_Y_CALIBRATION
            elif name == "轮廓标定":
                self.draw_mode = ImageUtil.ID_OUTLINE_CALIBRATION
            elif name == "调整车轴":
                self.draw_mode = ImageUtil.ID_AXLE_X_CALIBRATION
            elif name == "添加车轴":
                self.draw_mode = ImageUtil.ID_NEW_AXLE_CALIBRATION
            elif name == "分类标签":
                self.draw_mode = ImageUtil.ID_G_LABEL
            elif name == "目标检测标签":
                self.draw_mode = ImageUtil.ID_B_LABEL
            elif name == "分割标签":
                self.draw_mode = ImageUtil.ID_P_LABEL
            else:
                self.draw_mode = ImageUtil.ID_NONE
        else:
            self.draw_mode = mode

    def set_image(self, filepath):
        if os.path.exists(filepath):
            self.to_show = wx.Bitmap(filepath)

    def on_left_down(self, event):
        self.CaptureMouse()
        self.start_pos = event.GetPosition()
        self.SetFocus()

    def on_right_down(self, event):
        self.CaptureMouse()
        self.move_start_pos = event.GetPosition()
        self.SetFocus()

    def on_right_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.show_pos = self.show_pos[0] + self.diff[0], self.show_pos[1] + self.diff[1]

    def draw_background_image(self, dc):
        if self.to_show is not None:
            img = self.to_show.ConvertToImage()
            now_ratio = self.get_now_ratio()
            # self.show_pos = self.show_pos[0]*(1+now_ratio), self.show_pos[1]*(1+now_ratio)
            if now_ratio != 0:
                img = img.Scale(self.GetClientSize()[0] * (1 + now_ratio), self.GetClientSize()[1] * (1 + now_ratio))
            else:
                img = img.Scale(self.GetClientSize()[0], self.GetClientSize()[1])
            bmp = wx.Bitmap(img)
            dc.Clear()
            dc.DrawBitmap(bmp, self.show_pos[0] + self.diff[0], self.show_pos[1] + self.diff[1])

    def draw_car_calibration(self, dc, id):
        # 车厢
        try:
            self.draw_rect(dc, id=id, color=wx.RED, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_axel_y_calibration(self, dc, id):
        # 车轴
        try:
            x, y = self.GetClientSize()
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            self.draw_line(dc, p1, p2, id=id, color=wx.YELLOW, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_axel_x_calibration(self, dc, id):
        # 调整车轴
        try:
            x, y = self.GetClientSize()
            # x
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            self.draw_line(dc, p1, p2, id=id, color=wx.YELLOW, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_rail_y_calibration(self, dc, id):
        # 铁轨
        try:
            x, y = self.GetClientSize()
            p1 = 0, self.end_pos[1]
            p2 = x, self.end_pos[1]
            self.draw_line(dc, p1, p2, id=id, color=wx.BLUE, style=wx.PENSTYLE_SOLID)
        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_rect(self, dc, rect=None, id=ImageUtil.ID_NONE, color=wx.RED, style=wx.PENSTYLE_SOLID):  # 画矩形透明区域
        # dc -> 绘图上下文，必需
        # rect -> wx.Rect类型，由外部传入
        # id -> int类型，标识图形类别
        # color -> 颜色
        # style -> 样式
        if self.start_pos is None or self.end_pos is None:
            return
        try:
            odc = wx.DCOverlay(self.overlay, dc)
            odc.Clear()
            if 'wxMac' not in wx.PlatformInfo:
                dc = wx.GCDC(dc)
            dc.SetPen(wx.Pen(colour=color,
                             width=self.overlayPenWidth.GetValue(),
                             style=style))

            bc = wx.RED
            bc = wx.Colour(bc.red, bc.green, bc.blue, 0x80)
            dc.SetBrush(wx.Brush(bc))
            if rect is None:
                rect = wx.Rect(topLeft=self.start_pos, bottomRight=self.end_pos)
            dc.DrawRectangle(rect)
            self.objects[id].append(rect)

        except Exception as e:
            Util.LOG.error(repr(e))

    def draw_line(self, dc, p1, p2, id=ImageUtil.ID_NONE, color=wx.RED, style=wx.PENSTYLE_SOLID):
        dc.SetPen(wx.Pen(colour=color,
                         width=self.overlayPenWidth.GetValue(),
                         style=style))
        x1, y1 = p1
        x2, y2 = p2
        dc.DrawLine(
            x1,
            y1,
            x2,
            y2
        )
        self.objects[id].append(
            [
                id,
                p1,
                p2
            ]
        )

    def on_mouse_move(self, event):
        # 绘图
        if event.Dragging() and event.LeftIsDown():
            self.end_pos = event.GetPosition()
            self.Refresh()

        # 拖动
        if event.Dragging() and event.RightIsDown():
            self.move_end_pos = event.GetPosition()
            self.diff = self.move_end_pos[0] - self.move_start_pos[0], self.move_end_pos[1] - self.move_start_pos[1]
            self.Refresh()

    def on_erase(self, event):
        pass

    def on_left_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.start_pos = self.end_pos
        self.end_pos = event.Position
        # self.Refresh()

    def on_size(self, event=None):
        if event:
            event.Skip()
        self.Refresh()

    def draw_objects(self, dc):
        # if "rect" in self.objects.keys():
        #     for rect in self.objects["rect"]:
        #         dc.DrawRectangle(rect)
        pass

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.draw_background_image(dc)
        if self.draw_mode == ImageUtil.ID_CAR_CALIBRATION:
            self.draw_rect(dc)


if __name__ == '__main__':
    app = wx.App()
    win = wx.Frame(None, title="图像处理", size=(800, 600))
    file_path = 'D:\\code\\jetbrains\\pycharm\\test\\C70_202.202.202.3_20170420073727_L006_6.jpg'
    p = test(win, file_path)
    # p = ImagePanel(win, file_path)
    win.Show()
    app.MainLoop()