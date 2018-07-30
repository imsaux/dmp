# encoding=utf-8

import os

class CarClassification:
    def __init__(self, dir_path):
        self.image_files = dict()
        self.index_files = dict()
        self.index_datas = dict()
        for _root, _dir, _file in os.walk(dir_path, topdown=False):
            if _root != dir_path:
                date = _root.split("\\")[-1]
                line = _root.split("\\")[-2]
                if line not in self.image_files.keys():
                    self.image_files[line] = dict()
                if date not in self.image_files[line].keys():
                    self.image_files[line][date] = list()
                if line not in self.index_files.keys():
                    self.index_files[line] = dict()
            for _f in _file:
                if os.path.splitext(_f)[1].upper() == '.JPG':
                    self.image_files[line][date].append(os.path.join(_root, _f))
                if _f == "index.txt":
                    self.index_files[line][date] = os.path.join(_root, "index.txt")
            # break
        if len(self.index_files.keys())>0:
            self.analysis_index()
            self.rename()
        else:
            pass

    @property
    def IndexData(self):
        return self.index_datas

    def analysis_index(self):
        for line in self.index_files.keys():
            for date in self.index_files[line].keys():
                _is_D = False
                with open(self.index_files[line][date], "r") as fr:
                    index_data = fr.readlines()
                    if line not in self.index_datas.keys():
                        self.index_datas[line] = dict()
                    if date not in self.index_datas[line].keys():
                        self.index_datas[line][date] = dict()
                    for _l in index_data:
                        if "\t" in _l:
                            if "*" in _l:
                                _l.replace("*", "#")
                            l = _l.split("\t")
                            self.index_datas[line][date][l[0]] = dict()
                            self.index_datas[line][date][l[0]]["code"] = l[3]
                            self.index_datas[line][date][l[0]]["speed"] = l[1]
                            self.index_datas[line][date][l[0]]["width"] = l[2]
                            self.index_datas[line][date][l[0]]["line"] = line
                            self.index_datas[line][date][l[0]]["date"] = date
                            if l[3][0] == 'J':
                                if ' D ' == l[3][12:15]: # 动车
                                    _is_D = True
                                self.index_datas[line][date]["trainno"] = l[3][12:19]
                                self.index_datas[line][date][l[0]]["carno"] = l[3][4:8]
                                self.index_datas[line][date][l[0]]["kind"] = l[3][1:4]
                                self.index_datas[line][date][l[0]]["type"] = ''
                                self.index_datas[line][date][l[0]]["property"] = 'J'
                            elif l[3][0] == 'K':
                                self.index_datas[line][date][l[0]]["carno"] = l[3][6:13]
                                self.index_datas[line][date][l[0]]["kind"] = l[3][4:6]
                                self.index_datas[line][date][l[0]]["type"] = l[3][1:4]
                                self.index_datas[line][date][l[0]]["property"] = l[3][0]
                            elif l[3].count('X') == 20:
                                if _is_D:
                                    self.index_datas[line][date][l[0]]["kind"] = ""
                                    self.index_datas[line][date][l[0]]["type"] = "D"
                                    self.index_datas[line][date][l[0]]["property"] = "D"
                                else:
                                    self.index_datas[line][date][l[0]]["kind"] = "##"
                                    self.index_datas[line][date][l[0]]["type"] = "##"
                                    self.index_datas[line][date][l[0]]["property"] = "#"
                            else:
                                self.index_datas[line][date][l[0]]["carno"] = l[3][7:14]
                                self.index_datas[line][date][l[0]]["kind"] = l[3][2:7]
                                self.index_datas[line][date][l[0]]["type"] = l[3][1]
                                self.index_datas[line][date][l[0]]["property"] = l[3][0]

    def rename(self):
        for line in self.image_files.keys():
            for date in self.image_files[line].keys():
                for img in self.image_files[line][date]:
                    no = img.split('_')[1].split('.')[0]
                    try:
                        info = self.index_datas[line][date][no]
                        _new = os.path.dirname(img) + '\\' + '_'.join(
                            [
                                info['property'] + info['type'] + info['kind'].strip(),
                                info['line'],
                                info['date'],
                                os.path.basename(img)
                            ])
                        os.rename(
                            img,                            
                            _new
                        )
                    except Exception as e:
                        pass


if __name__ == "__main__":
    _dir = "E:\\data\\work\\车型分类及重命名规则\\test\\202.202.202.2"
    cc = CarClassification(_dir)


