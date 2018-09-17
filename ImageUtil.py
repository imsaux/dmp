# encode=utf-8

from PIL import Image, ImageStat
from tkinter.filedialog import *
from xml.etree import ElementTree as ET
import codecs
import numpy as np
import cv2
import json
import Util
import random


ID_NONE = 1
ID_CAR_CALIBRATION = 2
ID_AXLE_Y_CALIBRATION = 3
ID_AXLE_X_CALIBRATION = 4
ID_RAIL_Y_CALIBRATION = 5
ID_B_LABEL = 6 # 目标检测
ID_G_LABEL = 7 # 分类
ID_P_LABEL = 8 # 分割
ID_OUTLINE_CALIBRATION = 9
ID_NEW_AXLE_CALIBRATION = 10

PNG_PALETTE = [[254, 254, 254], [128, 0, 0], [0, 128, 0], [128, 128, 0], [0, 0, 128], [128, 0, 128], [0, 128, 128], [218, 178, 115], [192, 220, 192], [166, 202, 240], [10, 10, 10], [11, 11, 11], [12, 12, 12], [13, 13, 13], [14, 14, 14], [15, 15, 15], [16, 16, 16], [17, 17, 17], [18, 18, 18], [19, 19, 19], [20, 20, 20], [21, 21, 21], [22, 22, 22], [23, 23, 23], [24, 24, 24], [25, 25, 25], [26, 26, 26], [27, 27, 27], [28, 28, 28], [29, 29, 29], [30, 30, 30], [31, 31, 31], [32, 32, 32], [33, 33, 33], [34, 34, 34], [35, 35, 35], [36, 36, 36], [37, 37, 37], [38, 38, 38], [39, 39, 39], [40, 40, 40], [41, 41, 41], [42, 42, 42], [43, 43, 43], [44, 44, 44], [45, 45, 45], [46, 46, 46], [47, 47, 47], [48, 48, 48], [49, 49, 49], [50, 50, 50], [51, 51, 51], [52, 52, 52], [53, 53, 53], [54, 54, 54], [55, 55, 55], [56, 56, 56], [57, 57, 57], [58, 58, 58], [59, 59, 59], [60, 60, 60], [61, 61, 61], [62, 62, 62], [63, 63, 63], [64, 64, 64], [65, 65, 65], [66, 66, 66], [67, 67, 67], [68, 68, 68], [69, 69, 69], [70, 70, 70], [71, 71, 71], [72, 72, 72], [73, 73, 73], [74, 74, 74], [75, 75, 75], [76, 76, 76], [77, 77, 77], [78, 78, 78], [79, 79, 79], [80, 80, 80], [81, 81, 81], [82, 82, 82], [83, 83, 83], [84, 84, 84], [85, 85, 85], [86, 86, 86], [87, 87, 87], [88, 88, 88], [89, 89, 89], [90, 90, 90], [91, 91, 91], [92, 92, 92], [93, 93, 93], [94, 94, 94], [95, 95, 95], [96, 96, 96], [97, 97, 97], [98, 98, 98], [99, 99, 99], [100, 100, 100], [101, 101, 101], [102, 102, 102], [103, 103, 103], [104, 104, 104], [105, 105, 105], [106, 106, 106], [107, 107, 107], [108, 108, 108], [109, 109, 109], [110, 110, 110], [111, 111, 111], [112, 112, 112], [113, 113, 113], [114, 114, 114], [115, 115, 115], [116, 116, 116], [117, 117, 117], [118, 118, 118], [119, 119, 119], [120, 120, 120], [121, 121, 121], [122, 122, 122], [123, 123, 123], [124, 124, 124], [125, 125, 125], [126, 126, 126], [127, 127, 127], [128, 128, 128], [129, 129, 129], [130, 130, 130], [131, 131, 131], [132, 132, 132], [133, 133, 133], [134, 134, 134], [135, 135, 135], [136, 136, 136], [137, 137, 137], [138, 138, 138], [139, 139, 139], [140, 140, 140], [141, 141, 141], [142, 142, 142], [143, 143, 143], [144, 144, 144], [145, 145, 145], [146, 146, 146], [147, 147, 147], [148, 148, 148], [149, 149, 149], [150, 150, 150], [151, 151, 151], [152, 152, 152], [153, 153, 153], [154, 154, 154], [155, 155, 155], [156, 156, 156], [157, 157, 157], [158, 158, 158], [159, 159, 159], [160, 160, 160], [161, 161, 161], [162, 162, 162], [163, 163, 163], [164, 164, 164], [165, 165, 165], [166, 166, 166], [167, 167, 167], [168, 168, 168], [169, 169, 169], [170, 170, 170], [171, 171, 171], [172, 172, 172], [173, 173, 173], [174, 174, 174], [175, 175, 175], [176, 176, 176], [177, 177, 177], [178, 178, 178], [179, 179, 179], [180, 180, 180], [181, 181, 181], [182, 182, 182], [183, 183, 183], [184, 184, 184], [185, 185, 185], [186, 186, 186], [187, 187, 187], [188, 188, 188], [189, 189, 189], [190, 190, 190], [191, 191, 191], [192, 192, 192], [193, 193, 193], [194, 194, 194], [195, 195, 195], [196, 196, 196], [197, 197, 197], [198, 198, 198], [199, 199, 199], [200, 200, 200], [201, 201, 201], [202, 202, 202], [203, 203, 203], [204, 204, 204], [205, 205, 205], [206, 206, 206], [207, 207, 207], [208, 208, 208], [209, 209, 209], [210, 210, 210], [211, 211, 211], [212, 212, 212], [213, 213, 213], [214, 214, 214], [215, 215, 215], [216, 216, 216], [217, 217, 217], [218, 218, 218], [219, 219, 219], [220, 220, 220], [221, 221, 221], [222, 222, 222], [223, 223, 223], [224, 224, 224], [225, 225, 225], [226, 226, 226], [227, 227, 227], [228, 228, 228], [229, 229, 229], [230, 230, 230], [231, 231, 231], [232, 232, 232], [233, 233, 233], [234, 234, 234], [235, 235, 235], [236, 236, 236], [237, 237, 237], [238, 238, 238], [239, 239, 239], [240, 240, 240], [241, 241, 241], [242, 242, 242], [243, 243, 243], [244, 244, 244], [245, 245, 245], [246, 246, 246], [247, 247, 247], [248, 248, 248], [249, 249, 249], [250, 250, 250], [251, 251, 251], [252, 252, 252], [253, 253, 253], [254, 254, 254], [255, 255, 255]]


# png -> png图片pil.image对象
# alpha -> alpha通道值（0~255）
# dst_png_path -> 保存路径
def set_png_alpha(png, alpha, dst_png_path):
	if isinstance(alpha, list) and png is not None and isinstance(png, Image):
		try:
			data = png.getdata()
			i = 0
			for v in alpha:
				data.putpalettealpha(i, v)
				i += 1
			png.putdata(data)
			png.save(dst_png_path)
			return True
		except Exception as e:
			Util.LOG.error(repr(e))
			return False


# p -> xy坐标
# ratio -> 缩放系数
def coord_to_zoom(p, ratio):
	return p[0]*ratio, p[1]*ratio


# p -> xy坐标
# ratio -> 缩放系数
def coord_to_origin(p, ratio):
	return p[0]/ratio, p[1]/ratio


# 标签缩放
def label_zoom(pic_list, data_list): # todo 重构
    d = dict()
    for i in range(len(data_list)):
        data = data_list[i].split(' ')
        t = [int(i) for i in data[4:8]]
        for j in range(len(pic_list)):
            l_image = pic_list[j].split('_')
            l_image[-1] = l_image[-1][:-4]
            l_image.remove(l_image[0])
            s = [int(k) for k in l_image[:-1]]
            factor = float(l_image[-1])*0.05
            if t[0] >= s[0] and t[2] <= s[2] and t[1] >= s[1] and t[3] <= s[3]:
                new_coordinate_int = [t[0] - s[0],
                                      t[1] - s[1], t[2] - s[0], t[3] - s[1]]
                new_coordinate_int_factor = [
                    int(factor * k * 0.05) for k in new_coordinate_int]
                new_coordinate_str = [str(i)
                                      for i in new_coordinate_int_factor]
                data[4:8] = new_coordinate_str
                new_data_str = ' '.join(data)
                if j in d.keys():
                    d[j].append(new_data_str)
                else:
                    d[j] = [new_data_str]
    # print(d)
    return d
#
# pic_list = ['0886938e6d104cc584a213fc6c4127dc_0_500_1000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_1000_500_2000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_2000_500_3000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_3000_500_4000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_4000_500_5000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_5000_500_6000_1500_15.jpg',
#             '0886938e6d104cc584a213fc6c4127dc_5818_500_6818_1500_15.jpg']
# data = ['door 0.0 0 0.0 1227 680 1864 1365 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
#         'door 0.0 0 0.0 2254 603 2841 850 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
#         'door 0.0 0 0.0 3151 825 3864 1336 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
#         'window 0.0 0 0.0 4165 586 4844 895 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
#         'window 0.0 0 0.0 3264 659 3767 1208 0.0 0.0 0.0 0.0 0.0 0.0 0.0']
#
# print(imagezoom(pic_list, data))


class json_handle():
	def __init__(self, calibrationFile=None):
		self.data = None
		self.data_source_is_json = False
		self.readJSON(calibrationFile)

	def export(self):
		if self.data_source_is_json:
			self.export2JSON()
		else:
			self.export2XML()

	def readJSON(self, calibrationFile):
		if calibrationFile is not None and os.path.exists(calibrationFile):
			with open(calibrationFile, 'r') as fpRead:
				self.data = json.load(fpRead)
				self.data_source_is_json = True
				self._baseName = os.path.splitext(calibrationFile)[0]

	def export2JSON(self):
		with open('calibration.json', 'w') as fpWrite:
			json.dump(self.data, fpWrite, indent=4)

	@property
	def Data(self):
		return self.data

	def export2XML(self, xmlFile=None):
		_ImagingProperties = ET.Element('ImagingProperties')
		for line in self.data.keys():
			_CameraPosition = ET.SubElement(_ImagingProperties, 'CameraPosition')
			_CameraPosition.set('line', line)
			for side in self.data[line]:
				_lphototype = ET.SubElement(_CameraPosition, 'phototype')
				_lphototype.set('imgtype', side)
				for items in self.data[line][side]:
					if isinstance(self.data[line][side][items], dict):
						kind = ET.SubElement(_lphototype, 'carcz')
						kind.set('cztype', items)
						_x = ET.SubElement(kind, 'X_carbody')
						_x.text = str(self.data[line][side][items]['X_carbody'])
						_y = ET.SubElement(kind, 'Y_carbody')
						_y.text = str(self.data[line][side][items]['Y_carbody'])
						_w = ET.SubElement(kind, 'width_carbody')
						_w.text = str(self.data[line][side][items]['width_carbody'])
						_h = ET.SubElement(kind, 'height_carbody')
						_h.text = str(self.data[line][side][items]['height_carbody'])
					elif isinstance(self.data[line][side][items], int):
						_newOffsetX = ET.Element(items)
						_newOffsetX.text = str(self.data[line][side][items])
						_lphototype.insert(0, _newOffsetX)
		tree = ET.ElementTree(element=_ImagingProperties)
		if xmlFile is not None:
			tree.write(xmlFile)
		else:
			tree.write(self._baseName + '.config')

	def _readXML(self, xmlFile):
		import re
		tree = None
		self._baseName = os.path.splitext(xmlFile)[0]
		try:
			with codecs.open(xmlFile, 'r', 'gbk') as f:
				text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", f.read())
				tree = ET.ElementTree(ET.fromstring(text))
		except ET.ParseError:
			pass
		finally:
			return tree

	def fromXML(self, xmlFile):
		_data = dict()
		tree = self._readXML(xmlFile)
		for line in tree.getroot():
			_data[line.get('line')] = dict()
			for side in line:
				_data[line.get('line')][side.get('imgtype')] = dict()
				for items in side:
					if len(items.getchildren()) > 0:
						_new_cztype = dict()
						for item in items:
							_new_cztype[item.tag] = round(int(item.text))
						_data[line.get('line')][side.get('imgtype')][items.get('cztype')] = _new_cztype
					else:
						_data[line.get('line')][side.get('imgtype')][items.tag] = round(int(items.text))
		self.data_source_is_json = False
		self.data = _data

	def carbody(self, kind, line, side, _new=None):
		if _new is None:
			if line in self.data and side in self.data[line] and kind in self.data[line][side]:
				return self.data[line][side][kind]
			else:
				return None
		else:
			if line not in self.data:
				self.data[line] = dict()
			if side not in self.data[line]:
				self.data[line][side] = dict()
			if kind not in self.data[line][side]:
				self.data[line][side][kind] = dict()

			self.data[line][side][kind] = _new

	def axel(self, line, side, _new=None, Z=False):
		_item = 'train_axle_xoffset'
		if Z:
			_item = 'zx_train_axle_xoffset'
		if _new is None:
			if line in self.data \
					and side in self.data[line] \
					and _item in self.data[line][side]:
				return self.data[line][side][_item]
			else:
				return None
		else:
			if line not in self.data:
				self.data[line] = dict()
			if side not in self.data[line]:
				self.data[line][side] = dict()
			self.data[line][side][_item] = _new

	def wheel(self, line, side, _new=None, Z=False):
		_item = 'train_axle_y'
		if Z:
			_item = 'zx_train_axle_y'
		if _new is None:
			if line in self.data and side in self.data[line] and _item in self.data[line][side]:
				return self.data[line][side][_item]
			else:
				return None
		else:
			if line not in self.data:
				self.data[line] = dict()
			if side not in self.data[line]:
				self.data[line][side] = dict()
			self.data[line][side][_item] = _new

	def rail(self, line, side, _new=None, Z=False):
		_item = 'rail_y'
		if Z:
			_item = 'zx_rail_y'
		if _new is None:
			if line in self.data and side in self.data[line] and _item in self.data[line][side]:
				return self.data[line][side][_item]
			else:
				return None
		else:
			if line not in self.data:
				self.data[line] = dict()
			if side not in self.data[line]:
				self.data[line][side] = dict()
			self.data[line][side][_item] = _new

	def outline(self, line, kind, _new=None):
		_item_top = 'Y_carbody'
		_item_bottom = 'height_carbody'
		_item_w = 'width_carbody'
		_item_h = 'X_carbody'

		if _new is not None and hasattr(_new, '__len__'):
			if len(_new) >= 2:
				if int(_new[0]) > int(_new[1]):
					_new[0], _new[1] = _new[1], _new[0]
				# _new[1] -= _new[0]
				if line not in self.data:
					self.data[line] = dict()
				if 'T' not in self.data[line]:
					self.data[line]['T'] = dict()
				if kind not in self.data[line]['T']:
					self.data[line]['T'][kind] = dict()
				self.data[line]['T'][kind][_item_top] = _new[0]
				self.data[line]['T'][kind][_item_bottom] = _new[1]
				self.data[line]['T'][kind][_item_w] = 30000
				self.data[line]['T'][kind][_item_h] = 0
		else:
			if line in self.data \
					and 'T' in self.data[line] \
					and kind in self.data[line]['T']:
				return self.data[line]['T'][kind][_item_top], self.data[line]['T'][kind][_item_bottom]
			else:
				return 0, 0

	def oneclick(self, lst_cztype, autoCalibrationParams, line, side):
		for carz in lst_cztype:
			self.data[line][side][carz]['X_carbody'] += autoCalibrationParams[0]
			self.data[line][side][carz]['Y_carbody'] += autoCalibrationParams[1]
			self.data[line][side][carz]['width_carbody'] = round(
				self.data[line][side][carz]['width_carbody'] * autoCalibrationParams[2])
			self.data[line][side][carz]['height_carbody'] = round(
				self.data[line][side][carz]['height_carbody'] * autoCalibrationParams[3])


class ImageBinaryFunc:
	def __init__(self, file_path):
		self.pic_path = file_path
		self.origin_wheel_data = None

	def read_pic_data(self):
		try:
			data = None
			with open(self.pic_path, 'rb') as fr:
				data = fr.read()
		except Exception as e:
			# self.log.info(repr(e))
			pass
		finally:
			return data

	def get_pic_wheel_data(self, b_data):
		# 获取图片车轮二进制数据
		s_wheel = "(\<Wheel\d{1,2}\s+\=\s+\-?\d+\>)+"
		s_wheel_value = "(\-?\d+)"
		try:
			l_wheels = [x for x in re.split(s_wheel, str(b_data)) if "Wheel" in x]
			self.origin_wheel_data = l_wheels
			tmp = [re.split(s_wheel_value, y)[3] for y in l_wheels]
			l_wheels_value = [int(x) for x in tmp if x != "-1"]
			return l_wheels_value
		except:
			return None

	def get_pic_calibration_data(self, b_data):
		# 获取图片标定二进制数据

		dt_calibration_regex = {
			"Cwheelcenter": "\<Cwheelcenter\s\=\s\-?\d+\>",
			"Cwheeloffset": "\<Cwheeloffset\s\=\s\-?\d+\>",
			"Ctop": "\<Ctop\s\=\s\-?\d+\>",
			"Cbottom": "\<Cbottom\s\=\s\-?\d+\>",
			"Cleft": "\<Cleft\s\=\s\-?\d+\>",
			"Cright": "\<Cright\s\=\s\-?\d+\>",
			"Crail": "\<Crail\s\=\s\-?\d+\>"
		}
		try:
			self.pic_origin_calibration_data = dict()
			for k, v in dt_calibration_regex.items():
				try:
					self.pic_origin_calibration_data[k] = re.search(v, str(b_data)).group()
				except Exception as e:
					pass
		except Exception as e:
			self.pic_origin_calibration_data = None

	def get_pic_calibration_value_data(self):
		# 从二进制中获取十进制数据
		if self.pic_origin_calibration_data is None:
			self.pic_calibration_value = None
		else:
			dt_calibration_value_regex = "(\-?\d+)"
			calibration_value_data = {k: int(re.search(dt_calibration_value_regex, v).group()) for k, v in
			                          self.pic_origin_calibration_data.items()}
			if '_T' in self.pic_path:
				self.pic_calibration_value = [
					calibration_value_data["Cleft"] if "Cleft" in calibration_value_data.keys() else 0,
					calibration_value_data["Ctop"] if "Ctop" in calibration_value_data.keys() else 0,
					calibration_value_data["Cright"] if "Cright" in calibration_value_data.keys() else 0,
					calibration_value_data["Cbottom"] if "Cbottom" in calibration_value_data.keys() else 0,
					calibration_value_data["Cwheelcenter"] if "Cwheelcenter" in calibration_value_data.keys() else 0,
					calibration_value_data["Cwheeloffset"] if "Cwheeloffset" in calibration_value_data.keys() else 0,
					calibration_value_data["Crail"] if "Crail" in calibration_value_data.keys() else 0
				]
			else:
				self.pic_calibration_value = [
					calibration_value_data["Cleft"] if "Cleft" in calibration_value_data.keys() else 0,
					calibration_value_data["Ctop"] if "Ctop" in calibration_value_data.keys() else 0,
					calibration_value_data["Cright"] if "Cright" in calibration_value_data.keys() else 0 -
					                                                                                   calibration_value_data[
						                                                                                   "Cleft"] if "Cleft" in calibration_value_data.keys() else 0,
					calibration_value_data["Cbottom"] if "Cbottom" in calibration_value_data.keys() else 0 -
					                                                                                     calibration_value_data[
						                                                                                     "Ctop"] if "Ctop" in calibration_value_data.keys() else 0,
					calibration_value_data["Cwheelcenter"] if "Cwheelcenter" in calibration_value_data.keys() else 0,
					calibration_value_data["Cwheeloffset"] if "Cwheeloffset" in calibration_value_data.keys() else 0,
					calibration_value_data["Crail"] if "Crail" in calibration_value_data.keys() else 0
				]

	def generate_pic_wheel_data(self, lt_new_value):
		tmp = "<Wheel%s = %s> "
		s_wheel_data = ""
		index = 1
		lt_new_value.sort()
		for x in lt_new_value:
			s_wheel_data += tmp % (str(index), x)
			index += 1
		self.current_pic_binary_data += s_wheel_data.encode()

	def generate_pic_calibration_data(self, dt_new_value):
		# 生成二进制标定修改数据
		dt_calibration_str = {
			"Cwheelcenter": "<Cwheelcenter = %s>",
			"Cwheeloffset": "<Cwheeloffset = %s>",
			"Ctop": "<Ctop = %s>",
			"Cbottom": "<Cbottom = %s>",
			"Cleft": "<Cleft = %s>",
			"Cright": "<Cright = %s>",
			"Crail": "<Crail = %s>",
		}
		if self.pic_origin_calibration_data is not None:
			r_old = {k: v for k, v in self.pic_origin_calibration_data.items()}
			r_new = {k: dt_calibration_str[k] % (v,) for k, v in dt_new_value.items()}
			for k, v in r_new.items():
				try:
					self.current_pic_binary_data = self.current_pic_binary_data.replace(r_old[k].encode(), v.encode())
				except Exception as e:
					self.current_pic_binary_data += r_new[k].encode()
		else:
			r_new = {k: dt_calibration_str[k] % (v,) for k, v in dt_new_value.items()}
			for k, v in r_new.items():
				self.current_pic_binary_data += v.encode()

	def save_pic_data(self):
		with open(self.pic_path, 'wb') as fw:
			fw.write(self.current_pic_binary_data)
		self.load_pic_binary()

	def remove_calibration(self):
		if self.pic_origin_calibration_data is not None:
			for k, v in self.pic_origin_calibration_data.items():
				self.current_pic_binary_data = self.current_pic_binary_data.replace(v.encode(), b"")
			self.save_pic_data()

	def remove_wheel(self):
		for l in self.origin_wheel_data:
			self.current_pic_binary_data = self.current_pic_binary_data.replace(l.encode(), b"")
		self.save_pic_data()

	def check_null_data(self, file):
		with open(file, "ab") as fa:
			if self.pic_calibration_value == [0, 0, 0, 0, 0, 0, 0] and self.calibrationHelper is not None:
				xywh = self.calibrationHelper.carbody(self.currentPicInfo[0], self.currentPicInfo[1],
				                                      self.currentPicInfo[2])
				if xywh is None:
					xywh = dict()
					xywh["X_carbody"] = 0
					xywh["Y_carbody"] = 0
					xywh["width_carbody"] = 0
					xywh["height_carbody"] = 0
				if '_T' not in self.pic_path:
					Cleft = "<Cleft = %s> " % (str(xywh["X_carbody"]))
					Ctop = "<Ctop = %s> " % (str(xywh["Y_carbody"]))
					Cright = "<Cright = %s> " % (str(xywh["X_carbody"]))
					Cbottom = "<Cbottom = %s> " % (str(xywh["height_carbody"]))
				else:
					Cleft = "<Cleft = %s> " % (str(xywh["X_carbody"]))
					Ctop = "<Ctop = %s> " % (str(xywh["Y_carbody"]))
					Cright = "<Cright = %s> " % (str(xywh["X_carbody"] + xywh["width_carbody"]))
					Cbottom = "<Cbottom = %s> " % (str(xywh["Y_carbody"] + xywh["height_carbody"]))
				fa.write(Cleft.encode())
				fa.write(Ctop.encode())
				fa.write(Cright.encode())
				fa.write(Cbottom.encode())

				_side = self.currentPicInfo[2]
				_line = str(self.currentPicInfo[1])
				_Z = True if '_Z' in self.pic_path else False
				try:
					_offset = int(self.calibrationHelper.axel(_line, _side, Z=_Z))
				except:
					_offset = 0
				try:
					_wheel = int(self.calibrationHelper.wheel(_line, _side, Z=_Z))
				except:
					_wheel = 0
				try:
					_raily = int(self.calibrationHelper.rail(_line, _side, Z=_Z))
				except:
					_raily = 0
				Cwheelcenter = "<Cwheelcenter = %s> " % (str(_wheel))
				Cwheeloffset = "<Cwheeloffset = %s> " % (str(_offset))
				Crail = "<Crail = %s> " % (str(_raily))
				fa.write(Cwheelcenter.encode())
				fa.write(Cwheeloffset.encode())
				fa.write(Crail.encode())
		self.load_pic_binary()

	def _getpicwheelinfo(self):
		self.pic_wheel_value = self.get_pic_wheel_data(self.current_pic_binary_data)

	def load_pic_binary(self):
		self.current_pic_binary_data = self.read_pic_data()
		self._getpicwheelinfo()
		self.get_pic_calibration_data(self.current_pic_binary_data)
		self.get_pic_calibration_value_data()

	def openCalibrationFile(self):
		_file_path = askopenfilename(title='请选择标定文件')
		if len(_file_path) > 0 and os.path.exists(_file_path):
			if os.path.splitext(_file_path)[1] == '.config':
				self.calibrationHelper = json_handle()
				self.calibrationHelper.fromXML(_file_path)
			if os.path.splitext(_file_path)[1] == '.json':
				self.calibrationHelper = json_handle(_file_path)
				print(self.calibrationHelper)

	def getPicInfo(self, pic):
		try:
			_lst = os.path.basename(pic).split('_')
			_kind = _lst[0]
			_line = str(int(_lst[1].split('.')[3]))
			# if self.is_sartas:
			#     _line = str(int(_line) - 1)
			if '#' in _lst[0]:
				_kind = _lst[0].replace('#', '*')
			if _lst[3][0] == 'Z':
				_side = _lst[3][1]
			else:
				_side = _lst[3][0]
		except:
			_kind = None
			_line = None
			_side = None
		finally:
			self.currentPicInfo = _kind, _line, _side
			return _kind, _line, _side


# left_top_pos -> 左上角点坐标
# mouse_pos -> 鼠标事件发生坐标
# ratio -> 缩放系数
def get_left_top_pos(left_top_pos, mouse_pos, ratio):
	_x = abs(left_top_pos[0]) + abs(mouse_pos[0])
	_y = abs(left_top_pos[1]) + abs(mouse_pos[1])
	origin_pos = coord_to_origin((_x, _y), ratio)
	new_left_top_pos = round(origin_pos[0]-mouse_pos[0]), round(origin_pos[1]-mouse_pos[1])
	return new_left_top_pos

#
# 图像处理
#


# 线性变换（取值范围从-50到50）
def linear_transformation(path_to_image, count, path_to_new_image):
	dct_process_result = dict()
	img = Image.open(path_to_image)
	mode = img.mode
	# 像素增量 列表
	s = [-50]
	for k in range(1, count - 1):
		l = int(s[k - 1] + 100 / (count - 1))
		s.append(l)
	s.append(50)
	for m in range(len(s)):
		if s[m] == 0:
			s[m] = 1

	if mode == 'L':
		pixel = img.load()
		total_pix = img.width * img.height
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('linear_transformation', mode, c)))
			for i in range(img.width):
				for j in range(img.height):
					pixel[i, j] += s[c]
					if pixel[i, j] > 255:
						pixel[i, j] = 255
					else:
						pixel[i, j] = pixel[i, j]
					dct_process_result[new_img_path] = (i + 1) * (j + 1) / total_pix
			img.save(new_img_path)
			img = Image.open(path_to_image)
			pixel = img.load()
	elif mode == 'RGB':
		img = cv2.imread(path_to_image, 1)
		imgb, imgg, imgr = cv2.split(img)
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('linear_transformation', mode, c)))
			total_pix = img.shape[0] * img.shape[1]
			b = imgb.copy()
			g = imgg.copy()
			r = imgr.copy()
			for i in range(0, img.shape[0]):
				for j in range(0, img.shape[1]):
					pix = int(b[i, j]) + s[c]
					if pix > 255:
						b[i, j] = 255
					elif pix < 0:
						b[i, j] = 0
					else:
						b[i, j] = pix
					pix = int(g[i, j]) + s[c]
					if pix > 255:
						g[i, j] = 255
					elif pix < 0:
						g[i, j] = 0
					else:
						g[i, j] = pix
					pix = int(r[i, j]) + s[c]
					if pix > 255:
						r[i, j] = 255
					elif pix < 0:
						r[i, j] = 0
					else:
						r[i, j] = pix
					dct_process_result[new_img_path] = (i + 1) * (j + 1) / total_pix
			img11 = cv2.merge([b, g, r])
			cv2.imwrite(new_img_path, img11)
	return dct_process_result


# 非线性变换（系数从0.1到0.6）
def non_linear_transformation(path_to_image, count, path_to_new_image):
	dct_process_result = dict()
	img = Image.open(path_to_image)
	mode = img.mode
	pixel = img.load()
	# 像素增量 列表
	s = [0.1]
	for k in range(1, count - 1):
		l = s[k - 1] + 0.5 / (count - 1)
		s.append(l)
	s.append(0.6)
	if mode == 'L':
		mean = int(ImageStat.Stat(img).mean[0])
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('non_linear_transformation', mode, c)))
			total_pix = img.width * img.height
			for i in range(img.width):
				for j in range(img.height):
					if pixel[i, j] > mean:
						dis = 255 - pixel[i, j]
						add = int(s[c] * dis)
						temp = pixel[i, j]
						temp += add
						if temp > 255:
							temp = 255
						else:
							temp = temp
						pixel[i, j] = temp
					elif pixel[i, j] < mean:
						dis = -pixel[i, j]
						add = int(s[c] * dis)
						temp = pixel[i, j]
						temp += add
						if temp < 0:
							temp = 0
						else:
							temp = temp
						pixel[i, j] = temp
					dct_process_result[new_img_path] = (i + 1) * (j + 1) / total_pix
			img.save(new_img_path)
			img = Image.open(path_to_image)
			pixel = img.load()
	elif mode == 'RGB':
		img = cv2.imread(path_to_image, 1)
		w = img.shape[0]
		h = img.shape[1]
		imgtemp = np.zeros((w, h), dtype=int)
		imgb, imgg, imgr = cv2.split(img)
		sum1 = np.sum(imgb, axis=None)
		sum2 = np.sum(imgg, axis=None)
		sum3 = np.sum(imgr, axis=None)
		for r1 in range(0, img.shape[0]):
			for c1 in range(0, img.shape[1]):
				sum_pix = np.sum(img[r1, c1])
				imgtemp[r1, c1] = sum_pix
		sumall = sum1 + sum2 + sum3
		ave = int(sumall / img.shape[0] / img.shape[1])
		max = 255 * 3
		for j in range(count):
			b = imgb.copy()
			g = imgg.copy()
			r = imgr.copy()
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('non_linear_transformation', mode, j)))
			total_pix = w * h
			for r2 in range(0, w):
				for c2 in range(0, h):
					if int(imgtemp[r2, c2]) > ave:
						dis = max - int(imgtemp[r2, c2])
						add = int(s[j] * dis / 3)
						pix = int(b[r2, c2]) + add
						if pix > 255:
							b[r2, c2] = 255
						else:
							b[r2, c2] = pix
						pix = int(g[r2, c2]) + add
						if pix > 255:
							g[r2, c2] = 255
						else:
							g[r2, c2] = pix
						pix = int(r[r2, c2]) + add
						if pix > 255:
							r[r2, c2] = 255
						else:
							r[r2, c2] = pix
					elif int(imgtemp[r2, c2]) < ave:
						dis = - int(imgtemp[r2, c2])
						add = int(s[j] * dis / 3)
						pix = int(b[r2, c2]) + add
						if pix < 0:
							b[r2, c2] = 0
						else:
							b[r2, c2] = pix
						pix = int(g[r2, c2]) + add
						if pix < 0:
							g[r2, c2] = 0
						else:
							g[r2, c2] = pix
						pix = int(r[r2, c2]) + add
						if pix < 0:
							r[r2, c2] = 0
						else:
							r[r2, c2] = pix
					dct_process_result[new_img_path] = (r2 + 1) * (c2 + 1) / total_pix
			img11 = cv2.merge([b, g, r])
			cv2.imwrite(new_img_path, img11)
	return dct_process_result


# 加噪（系数从0.01到0.11）
def imnoise(path_to_image, count, path_to_new_image):
	dct_process_result = dict()
	im = Image.open(path_to_image)
	mode = im.mode
	# 像素增量 列表
	s = [0.01]
	for k in range(1, count - 1):
		l = s[k - 1] + 0.1 / (count - 1)
		s.append(l)
	s.append(0.11)
	if mode == 'L':
		SP_NoiseImg = cv2.imread(path_to_image, 0)
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('imnoise', mode, c)))
			SP_NoiseNum = int(s[c] * SP_NoiseImg.shape[0] * SP_NoiseImg.shape[1])
			for i in range(SP_NoiseNum):
				randX = random.randint(0, SP_NoiseImg.shape[0] - 1)
				randY = random.randint(0, SP_NoiseImg.shape[1] - 1)
				pix = random.randint(200, 255)
				SP_NoiseImg[randX, randY] = pix
				dct_process_result[new_img_path] = (i + 1) / SP_NoiseNum
			cv2.imwrite(new_img_path, SP_NoiseImg)
			SP_NoiseImg = cv2.imread(path_to_image, 0)
	elif mode == 'RGB':
		SP_NoiseImg = cv2.imread(path_to_image, 1)
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('imnoise', mode, c)))
			SP_NoiseNum = int(s[c] * SP_NoiseImg.shape[0] * SP_NoiseImg.shape[1])
			for i in range(SP_NoiseNum):
				randX = random.randint(0, SP_NoiseImg.shape[0] - 1)
				randY = random.randint(0, SP_NoiseImg.shape[1] - 1)
				SP_NoiseImg[randX, randY][0] = random.randint(200, 255)
				SP_NoiseImg[randX, randY][1] = random.randint(200, 255)
				SP_NoiseImg[randX, randY][2] = random.randint(200, 255)
				dct_process_result[new_img_path] = (i + 1) / SP_NoiseNum
			cv2.imwrite(new_img_path, SP_NoiseImg)
			SP_NoiseImg = cv2.imread(path_to_image, 3)


#  高斯滤波去噪（系数从0.5到5）
def denoise(path_to_image, count, path_to_new_image):
	dct_process_result = dict()
	im = Image.open(path_to_image)
	mode = im.mode
	s = [0.5]
	for k in range(1, count - 1):
		l = s[k - 1] + 4.5 / (count - 1)
		s.append(l)
	s.append(5)
	if mode == 'L':
		img = cv2.imread(path_to_image, 0)
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('denoise', mode, c)))
			median = cv2.GaussianBlur(img, (5, 5), s[c])
			cv2.imwrite(new_img_path, median)

	elif mode == 'RGB':
		img = cv2.imread(path_to_image, 1)
		for c in range(count):
			new_img_path = os.path.normpath(os.path.join(path_to_new_image, path_to_image[:-4] + '_%s_%s_%s.jpg' % ('denoise', mode, c)))
			median = cv2.GaussianBlur(img, (5, 5), s[c])
			cv2.imwrite(new_img_path, median)
	return dct_process_result


if __name__ == '__main__':
	print(get_left_top_pos((100, -1), (3, 3), 1.75))