# encode = utf-8

import os.path
import Util
import threading
import ImageUtil

mutex = threading.Lock()


class _Classification:
	def __init__(self, file_path):
		self._file = file_path
		self.width = 0
		self.height = 0
		self.allow_vehicletype = []
		self.allow_side = []
		self.calibration_info = None
		self.wheel_info = None
		self.vehicletype = None
		self.side = None

		self.get_calibration()
		self.get_image_info()

	def get_image_info(self):
		try:
			_tmp = os.path.basename(self._file).split('_')
			if len(_tmp) == 5:
				if _tmp[0][0] in ['T', 'Q']:
					self.vehicletype = _tmp[0][1]
				elif _tmp[0][0] == 'K':
					self.vehicletype = 'K'
				elif _tmp[0][0] == 'D':
					self.vehicletype = 'D'
				else:
					self.vehicletype = 'J'
				self.side = _tmp[3][0]
		except Exception as e:
			Util.LOG.error(repr(e))

	def check(self):
		if self.vehicletype not in self.allow_vehicletype:
			return False
		if self.side not in self.allow_side:
			return False
		return True

	def get_calibration(self):
		try:
			ibf = ImageUtil.ImageBinaryFunc(self._file)
			if ibf is None:
				return
			pic_data = ibf.read_pic_data()
			# 获取图像标定信息
			ibf.get_pic_calibration_data(pic_data)
			ibf.get_pic_calibration_value_data()
			self.calibration_info = ibf.pic_calibration_value
			# 获取图像车轴信息
			self.wheel_info = ibf.get_pic_wheel_data(pic_data)
		except Exception as e:
			Util.LOG.error(repr(e))
			Util.LOG.debug(self._file)

	def cutting(self, count):
		pass # todo 裁剪


class Paulin(_Classification): # 篷布
	def __init__(self, file_path):
		super(Paulin, self).__init__(file_path)
		self.width = 256
		self.height = 256
		self.allow_vehicletype = ['C', 'N']
		self.allow_side = ['T',]
		self.checked = self.check()



class Pdoor(_Classification):
	def __init__(self, file_path):
		super(Pdoor, self).__init__(file_path)
		self.width = 250
		self.height = 500
		self.allow_vehicletype = ['P',]
		self.allow_side = ['L', 'R']
		self.checked = self.check()



if __name__ == '__main__':
	p = Paulin(r'D:\code\jetbrains\pycharm\dmp\tmp\TC70_202.202.202.2_20160510121653_L003_3.jpg')
	if p.checked:
		p.cutting(1)
	else:
		Util.LOG.info('非有效车型')
