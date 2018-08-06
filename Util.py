
# encode=utf-8

import re
from tkinter.filedialog import *
import json
from xml.etree import ElementTree as ET


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
                self.data[line]['T'][kind][_item_w] = -1
                self.data[line]['T'][kind][_item_h] = -1
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
            calibration_value_data = {k: int(re.search(dt_calibration_value_regex, v).group()) for k, v in self.pic_origin_calibration_data.items()}
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
                    calibration_value_data["Cright"] if "Cright" in calibration_value_data.keys() else 0 - calibration_value_data["Cleft"] if "Cleft" in calibration_value_data.keys() else 0,
                    calibration_value_data["Cbottom"] if "Cbottom" in calibration_value_data.keys() else 0 - calibration_value_data["Ctop"] if "Ctop" in calibration_value_data.keys() else 0,
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
            if self.pic_calibration_value == [0,0,0,0,0,0,0] and self.calibrationHelper is not None:
                xywh = self.calibrationHelper.carbody(self.currentPicInfo[0], self.currentPicInfo[1], self.currentPicInfo[2])
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
                    Cright = "<Cright = %s> " % (str(xywh["X_carbody"]+xywh["width_carbody"]))
                    Cbottom = "<Cbottom = %s> " % (str(xywh["Y_carbody"]+xywh["height_carbody"]))
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


