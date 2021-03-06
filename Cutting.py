# encode=utf-8

import os
import PIL.Image as pilImage
import copy
import ImageUtil
import uuid


class BaseCutting():
    def __init__(self, file_path, save_dir, scale):
        self.file_path = None
        self.img = None
        self.regions = list()
        self.train_info = None
        self.scale = scale

        if os.path.exists(file_path):
            self.file_path = file_path
            self.img = pilImage.open(self.file_path)
            _train_info = self.file_path.split('\\')
            self.basename = os.path.splitext(_train_info[-1])[0]
            self.basepath = save_dir

            tmp = _train_info[-1].split('_')
            if len(tmp) == 5:
                self.train_info = dict()
                self.train_info['kind'] = tmp[0]
                self.train_info['date'] = tmp[2]
                self.train_info['line'] = tmp[1]
                if len(tmp[3]) == 4:
                    self.train_info['side'] = tmp[3][0]
                elif len(tmp[3]) == 5:
                    self.train_info['side'] = tmp[3][:2]

    def cut(self):
        pass

    def save(self, img=None):
        _img = None
        for i in range(len(self.regions)):
            if img is None:
                _img = self.img.crop(self.regions[i])
            else:
                _img = img.crop(self.regions[i])
            _new_name = '_'.join([str(x) for x in self.regions[i]])
            path = os.path.join(self.basepath, uuid.uuid4().hex + '_' + _new_name + '_' + str(int(self.scale//0.05)) +  '.jpg')
            _img.save(path)


class K_DOOR_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)
        
    def cut(self, need_save=True):
        if self.img.width > 2048*2:
            _left = (0, 0, 2048, self.img.height)
            _right = ((self.img.width - 2048),0,self.img.width,self.img.height)
            new_img_left = self.img.crop(_left)
            new_img_right = self.img.crop(_right)
            self.regions.append(_left)
            self.regions.append(_right)
            if need_save:
                self.save()


class J_OBJECT_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)
        if self.train_info is not None and 'side' in self.train_info.keys():
            self.side = self.train_info['side']
        else:
            self.side = 'L'

    def cut(self, need_save=True):
        height = 256*2
        _rect = None
        if str(self.side).upper() == 'L':
            _rect = (
                int(self.img.width * 0.5),
                0,
                self.img.width,
                height
            )
        elif str(self.side).upper() == 'R':
            _rect = (
                0,
                0,
                self.img.width * 0.5,
                height
            )
        else:
            return

        _new_img = self.img.crop(_rect)

        block_step = 800*2
        last_x = 0
        offset = _rect[0]

        while last_x < _new_img.width - 200*2:
            if last_x + 1000*2 > _new_img.width:
                last_x = _new_img.width - 1000*2
            _rect = (last_x + offset, 0, last_x + 1000*2 + offset, _new_img.height)
            _new = _new_img.crop(_rect)
            last_x += 800*2
            self.regions.append(_rect)
        if need_save:
            self.save()


class Joint_OBJECT_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        carbration_x = 0
        carbration_y = 0
        carbration_width = 0
        carbration_height = 0
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        p.get_pic_calibration_data(p.read_pic_data())
        p.get_pic_calibration_value_data()
        if p.pic_calibration_value is None:
            return
        elif self.img.width <= 200*2:
            return
        else:
            carbration_x = p.pic_calibration_value[0]
            carbration_y = p.pic_calibration_value[1]
            carbration_width = p.pic_calibration_value[2]
            carbration_height = p.pic_calibration_value[3]
            if carbration_width == 0 or carbration_height == 0:
                return

        top = 0
        bottom = 0
        con_region_width = 200*2
        
        kind = self.train_info['kind'][1]
        if kind in ['C', 'P', 'W', 'B']:
            con_region_width = 300*2
        con_region_height = 0

        top = carbration_y - 100*2
        if top < 0:
            top = 0
        bottom = carbration_y + carbration_height + 100*2
        if bottom > self.img.height - 1:
            bottom = self.img.height - 1
        con_region_height = 960*2 if bottom - top > 960*2 else bottom - top 
        if con_region_height <= 0:
            return

        left = 0
        if left + con_region_width > self.img.width:
            left = self.img.width - con_region_width
        
        rect = (left, top, left + con_region_width, top + con_region_height)
        self.regions.append(rect)

        left = self.img.width - con_region_width
        if left < 0:
            left = 0
        if left + con_region_width > self.img.width:
            left = self.img.width - con_region_width
        
        rect = (left, top, left + con_region_width, top + con_region_height)
        self.regions.append(rect)        

        if need_save:
            self.save()


class T_OBJECT_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        img_top = None
        img_bottom = None
        carbration_x = 0
        carbration_y = 0
        carbration_width = 0
        carbration_height = 0
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        p.get_pic_calibration_data(p.read_pic_data())
        p.get_pic_calibration_value_data()
        if p.pic_calibration_value is None:
            return
        else:
            carbration_x = p.pic_calibration_value[0]
            carbration_y = p.pic_calibration_value[1]
            carbration_width = p.pic_calibration_value[2] - carbration_x + 1
            carbration_height = p.pic_calibration_value[3] - carbration_y + 1
            if carbration_width == 0 or carbration_height == 0:
                return
        
        region_x = 0
        region_y = 0
        region_width = self.img.width
        region_height = 256*2
        if region_height > self.img.height:
            return
        
        kind = self.train_info['kind'][1]

        # 车顶
        y_dis = 20*2
        if kind in ['C', 'P']:
            region_y = carbration_y - region_height + y_dis
            if region_y < 0:
                region_y = 0
            if region_y + region_height > self.img.height:
                region_y = self.img.height - region_height
            rect = (region_x, region_y, region_x + region_width, region_y + region_height)
            img_top = self.img.crop(rect)

        #车底
        y_dis = 100*2
        if kind in ['G']:
            y_dis = 50*2
        region_y = carbration_y + carbration_height - y_dis
        if region_y < 0:
            region_y = 0
        if region_y + region_height > self.img.height:
            region_y = self.img.height - region_height
        rect = (region_x, region_y, region_x + region_width, region_y + region_height)
        img_bottom = self.img.crop(rect)

        for img in [img_top, img_bottom]:
            if img is not None:
                last_x = 0
                while last_x < img.width - 200*2:
                    if last_x + 1000*2 > img.width:
                        last_x = img.width - 1000*2
                    _rect = (last_x, 0, last_x + 1000*2, img.height)
                    _new = img.crop(_rect)
                    last_x += 800*2
                    self.regions.append(_rect)
        
            if need_save:
                self.save(img)

        
class Top_ALL_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        carbration_y = 0
        carbration_height = 0
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        p.get_pic_calibration_data(p.read_pic_data())
        p.get_pic_calibration_value_data()
        if p.pic_calibration_value is None:
            return
        else:
            carbration_y = p.pic_calibration_value[1]
            carbration_height = p.pic_calibration_value[3] - carbration_y + 1

        rect = (0, carbration_y, self.img.width, carbration_y + carbration_height)
        self.regions.append(rect)
        if need_save:
            self.save()


class ZX_ANGLECOCK_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        axel_y = 0
        axel_x_offset = 0
        rail_y = 0 
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        data = p.read_pic_data()
        p.get_pic_calibration_data(data)
        p.get_pic_calibration_value_data()
        wheel = p.get_pic_wheel_data(data)
        if p.pic_calibration_value is None:
            return
        elif wheel is None:
            return
        else:
            axel_y = p.pic_calibration_value[4]
            axel_x_offset = p.pic_calibration_value[5]
            rail_y = p.pic_calibration_value[6]
        
        region_x = 0
        region_y = 0
        region_width = self.img.width
        region_height = 288*2

        if region_height > self.img.height:
            return

        axle_height = abs(rail_y - axel_y)
        region_y = axel_y - axle_height
        if region_y < 0:
            region_y = 0
        if region_y + region_height > self.img.height:
            region_y = self.img.height - region_height
        
        rect = (region_x, region_y, region_x + region_width, region_y + region_height)
        region_img = self.img.crop(rect)

        last_x = 0
        while last_x < region_img.width - 200*2:
            if last_x + 560*2 > region_img.width:
                last_x = region_img.width - 560*2
            _rect = (last_x, 0, last_x + 560*2, region_img.height)
            last_x += 360*2
            self.regions.append(_rect)

        if need_save:
            self.save()


class ZX_C_BTMBOLT_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        axel_y = 0
        axel_x_offset = 0
        rail_y = 0 
        carbration_x = 0
        carbration_y = 0
        carbration_width = 0
        carbration_height = 0
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        data = p.read_pic_data()
        p.get_pic_calibration_data(data)
        p.get_pic_calibration_value_data()
        wheel = p.get_pic_wheel_data(data)
        if p.pic_calibration_value is None:
            return
        elif wheel is None:
            return
        else:
            axel_y = p.pic_calibration_value[4]
            axel_x_offset = p.pic_calibration_value[5]
            rail_y = p.pic_calibration_value[6]
            carbration_x = p.pic_calibration_value[0]
            carbration_y = p.pic_calibration_value[1]
            carbration_width = p.pic_calibration_value[2] - carbration_x + 1
            carbration_height = p.pic_calibration_value[3] - carbration_y + 1

        region_x = 0
        region_y = 0
        region_width = self.img.width
        region_height = 288 * 2

        if region_height > self.img.height:
            return
        
        axel_height = abs(rail_y - axel_y)
        region_y = axel_y - axel_height*1.3 - region_height
        if region_y < 0:
            region_y = 0

        if region_y + region_height > self.img.height:
            region_y = self.img.height - region_height
        
        rect = (region_x, region_y, region_width, region_height)
        region_img = self.img.crop(rect)

        last_x = 0
        while last_x < region_img.width - 200*2:
            if last_x + 1096*2 > region_img.width:
                last_x = region_img.width - 1096*2
            _rect = (last_x, 0, last_x + 1096*2, region_img.height)
            last_x += 1096*2 - 200*2
            self.regions.append(_rect)

        if need_save:
            self.save()

        
class ZX_CHAINPIPE_Cutting(BaseCutting):
    def __init__(self, file_path, save_dir, scale):
        BaseCutting.__init__(self, file_path, save_dir, scale)

    def cut(self, need_save=True):
        axel_y = 0
        axel_x_offset = 0
        rail_y = 0 
        p = ImageUtil.ImageBinaryFunc(self.file_path)
        data = p.read_pic_data()
        p.get_pic_calibration_data(data)
        p.get_pic_calibration_value_data()
        wheel = p.get_pic_wheel_data(data)
        if p.pic_calibration_value is None:
            return
        elif wheel is None:
            return
        else:
            axel_y = p.pic_calibration_value[4]
            axel_x_offset = p.pic_calibration_value[5]
            rail_y = p.pic_calibration_value[6]
            wheel = [self.img.width - x - axel_x_offset for x in wheel]
            wheel.reverse()

        
        if len(wheel) != 4:
            return
        
        axel_length = 0
        axel_height = abs(rail_y - axel_y)

        base_point_x = 0
        base_point_y = axel_y
        chainpipe_x_ratio = 0
        chainpipe_y_ratio = 0.75
        chainpipe_width_ratio = 0
        chainpipe_height_ratio = 1.35

        if self.train_info['side'] == 'ZL':
            base_point_x = wheel[3]
            axel_length = abs(wheel[3] - wheel[2])
            if base_point_x < 0 or base_point_x >= self.img.width:
                return

            chainpipe_x_ratio = 0.22
            chainpipe_width_ratio = 1.25
            if self.train_info['kind'][1:3] == 'JSQ':
                chainpipe_x_ratio = 0.22
                chainpipe_width_ratio = 1.35
            elif self.train_info['kind'][1] == 'B':
                chainpipe_x_ratio = 0.22
                chainpipe_width_ratio = 0.95
        elif self.train_info['side'] == 'ZR':
            base_point_x = wheel[0]
            axel_length = abs(wheel[1] - wheel[0])
            if base_point_x < 0 or base_point_x >= self.img.width:
                return
            
            chainpipe_x_ratio = -1.48
            chainpipe_width_ratio = 1.25
            if self.train_info['kind'][1:3] == 'JSQ':
                chainpipe_x_ratio = -1.58
                chainpipe_width_ratio = 1.35
            elif self.train_info['kind'][1] == 'B':
                chainpipe_x_ratio = -1.18
                chainpipe_width_ratio = 0.95
        else:
            return # 非走行部图片退出
            
        _x = base_point_x + axel_length * chainpipe_x_ratio
        _w = axel_length * chainpipe_width_ratio
        _w = 1440 if _w > 1440 else _w
        _x = 0 if _x < 0 else _x
        _x = self.img.width - 2 if _x > self.img.width -1 else _x
        if _x + _w >= self.img.width:
            _w = self.img.width - _x

        _y = base_point_y - axel_height * chainpipe_y_ratio
        _h = axel_height * chainpipe_height_ratio
        _h = 720 if _h > 720 else _h
        _y = 0 if _y < 0 else _y
        _y = self.img.height - 2 if _y > self.img.height -1 else _y
        if _y + _h >= self.img.height:
            _h = self.img.height - _y

        rect = (round(_x), round(_y), round(_x + _w), round(_y + _h))
        self.regions.append(rect)

        if need_save:
            self.save()
            
if __name__ == '__main__':
#     # t = K_DOOR_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\KYW25G_202.202.202.3_20180215191704_R011_11.jpg')
#     # t = J_OBJECT_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\J239_202.202.202.3_20180215191704_L001_1.jpg')
    t = ZX_CHAINPIPE_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\QG60K_202.202.202.3_20171206112254_ZR016_16.jpg', r'd:\\', 0.78)
#     # t = Top_ALL_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\QG17DK_202.202.202.2_20170530051910_T014_14.jpg')
#     # t = T_OBJECT_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\TC70_202.202.202.2_20160510121653_L003_3.jpg')
#     # t = K_DOOR_Cutting(r'D:\code\jetbrains\pycharm\dmp\tmp\0527276.jpg')
    t.cut()
#     # pass
